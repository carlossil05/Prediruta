"""Google Places y mapas embebidos de la interfaz de PrediRuta.

Places se consulta desde Python para no exponer esa clave en el navegador. El
mapa sí necesita una clave pública porque Google Maps JavaScript se ejecuta en
el navegador; en producción esa clave debe restringirse por dominio.
"""

from __future__ import annotations

import json
from functools import lru_cache, partial
from unicodedata import normalize
from urllib.parse import quote

import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit_searchbox import st_searchbox


PLACES_AUTOCOMPLETE_URL = "https://places.googleapis.com/v1/places:autocomplete"
PLACES_DETAILS_URL = "https://places.googleapis.com/v1"

# El rectángulo evita sugerencias lejanas porque el alcance del proyecto es Bogotá.
BOGOTA_RECTANGLE = {
    "low": {"latitude": 4.48, "longitude": -74.22},
    "high": {"latitude": 4.825, "longitude": -74.00},
}


def _buscar_sugerencias(api_key: str, texto: str) -> list[tuple[str, dict]]:
    """Devuelve sugerencias de Places (New) listas para el control visual."""

    termino = texto.strip()
    if not api_key or len(termino) < 3:
        return []

    try:
        respuesta = requests.post(
            PLACES_AUTOCOMPLETE_URL,
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": (
                    "suggestions.placePrediction.place,"
                    "suggestions.placePrediction.text"
                ),
            },
            json={
                "input": termino,
                "includedRegionCodes": ["co"],
                "locationRestriction": {"rectangle": BOGOTA_RECTANGLE},
                "languageCode": "es",
                "regionCode": "CO",
            },
            timeout=8,
        )
        respuesta.raise_for_status()
    except requests.RequestException:
        # Una lista vacía representa ausencia temporal de resultados. No se
        # escribe la excepción para evitar que una URL revele la clave.
        return []

    opciones: list[tuple[str, dict]] = []
    for sugerencia in respuesta.json().get("suggestions", []):
        prediccion = sugerencia.get("placePrediction", {})
        etiqueta = prediccion.get("text", {}).get("text", "").strip()
        recurso = prediccion.get("place", "").strip()
        if etiqueta and recurso:
            opciones.append(
                (etiqueta, {"place_resource": recurso, "label": etiqueta})
            )
    return opciones


@lru_cache(maxsize=128)
def _obtener_detalle(api_key: str, recurso: str) -> dict | None:
    """Obtiene nombre, dirección y coordenadas del lugar elegido."""

    if not api_key or not recurso.startswith("places/"):
        return None
    try:
        respuesta = requests.get(
            f"{PLACES_DETAILS_URL}/{recurso}",
            headers={
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": (
                    "id,displayName,formattedAddress,location,addressComponents"
                ),
            },
            params={"languageCode": "es", "regionCode": "CO"},
            timeout=8,
        )
        respuesta.raise_for_status()
        lugar = respuesta.json()
    except requests.RequestException:
        return None

    ubicacion = lugar.get("location", {})
    if "latitude" not in ubicacion or "longitude" not in ubicacion:
        return None
    nombre = lugar.get("displayName", {}).get("text", "")
    direccion = lugar.get("formattedAddress") or nombre
    componentes_bogota = [
        componente
        for componente in lugar.get("addressComponents", [])
        if {"locality", "administrative_area_level_1"}
        & set(componente.get("types", []))
    ]
    es_bogota = any(
        normalize("NFKD", componente.get("longText", ""))
        .encode("ascii", "ignore")
        .decode()
        .casefold()
        == "bogota"
        for componente in componentes_bogota
    )
    return {
        "place_id": lugar.get("id", recurso.removeprefix("places/")),
        "name": nombre,
        "address": direccion,
        "lat": float(ubicacion["latitude"]),
        "lng": float(ubicacion["longitude"]),
        "es_bogota": es_bogota,
    }


def seleccionar_lugar(
    api_key: str,
    label: str,
    placeholder: str,
    kind: str,
    key: str,
) -> dict | None:
    """Muestra un autocompletado y devuelve solo una sugerencia confirmada."""

    icono = "📍" if kind == "origin" else "🏁"
    if not api_key:
        st.text_input(label, placeholder=placeholder, disabled=True, key=f"{key}_off")
        st.caption("Configura GOOGLE_PLACES_APIKEY para buscar lugares.")
        return None

    seleccion = st_searchbox(
        partial(_buscar_sugerencias, api_key),
        label=f"{icono}  {label}",
        placeholder=placeholder,
        key=key,
        debounce=280,
        edit_after_submit="option",
        clear_on_submit=False,
        help="Escribe al menos tres caracteres y elige una sugerencia de Google.",
        style_overrides={
            "clear": {"icon": "cross", "fill": "#607581"},
            "dropdown": {"fill": "#14777a"},
            "searchbox": {
                "control": {
                    "minHeight": "48px",
                    "borderRadius": "11px",
                    "borderColor": "#d7e1e5",
                    "boxShadow": "none",
                    "backgroundColor": "#ffffff",
                    "color": "#17324d",
                },
                "input": {"color": "#17324d", "backgroundColor": "transparent"},
                "option": {
                    "color": "#17324d",
                    "backgroundColor": "#ffffff",
                    "highlightColor": "#e8f4f3",
                },
                "placeholder": {"color": "#7a8c96"},
                "singleValue": {"color": "#17324d"},
                "menuList": {"maxHeight": "240px"},
            },
        },
    )
    if not isinstance(seleccion, dict):
        return None
    detalle = _obtener_detalle(api_key, seleccion.get("place_resource", ""))
    if detalle and not detalle["es_bogota"]:
        st.error(
            "Ese lugar está fuera de Bogotá. Elige otra sugerencia dentro "
            "del área urbana cubierta por PrediRuta."
        )
        return None
    return detalle


def _datos_json(datos: dict) -> str:
    """Serializa datos para un script HTML sin permitir cierre de etiqueta."""

    return json.dumps(datos, ensure_ascii=False).replace("<", "\\u003c")


def _documento_mapa(api_key: str, datos: dict) -> str:
    """Construye el documento aislado que dibuja el mapa de Google."""

    clave_url = quote(api_key, safe="")
    datos_json = _datos_json(datos)
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
html,body,#map{{height:100%;margin:0;width:100%;font-family:Arial,sans-serif}}
body{{background:#edf3f2}}
#shell{{border:1px solid #dce7e5;border-radius:18px;height:calc(100% - 2px);
  overflow:hidden;position:relative;box-shadow:0 10px 28px rgba(24,55,70,.08)}}
#empty{{background:rgba(255,255,255,.95);border-radius:12px;color:#49616e;
  left:50%;max-width:290px;padding:13px 16px;position:absolute;text-align:center;
  top:50%;transform:translate(-50%,-50%);z-index:4;font-size:13px;line-height:1.45}}
#empty:empty{{display:none}}
#legend{{align-items:center;background:rgba(255,255,255,.96);border-radius:11px;
  bottom:14px;box-shadow:0 4px 16px rgba(20,40,50,.16);display:none;gap:12px;
  left:14px;padding:9px 12px;position:absolute;z-index:3}}
#legend.show{{display:flex}} #legend span{{align-items:center;color:#425966;
  display:flex;font-size:11px;font-weight:700;gap:5px}}
#legend i{{border-radius:50%;height:9px;width:9px}}
.time-badge{{background:#fff;border:1px solid #d8e1e5;border-radius:9px;
  box-shadow:0 3px 9px rgba(20,40,50,.18);color:#284453;font-size:11px;
  font-weight:700;padding:4px 7px;white-space:nowrap}}
.segment-divider{{background:#fff;border:2px solid rgba(40,75,83,.42);border-radius:50%;
  box-shadow:0 1px 4px rgba(20,40,50,.14);height:7px;width:7px}}
</style></head><body><div id="shell"><div id="map"></div><div id="empty"></div>
<div id="legend"><span><i style="background:#2E8B57"></i>Bajo</span>
<span><i style="background:#F4A261"></i>Medio</span>
<span><i style="background:#D1495B"></i>Alto</span></div></div>
<script id="prediruta-data" type="application/json">{datos_json}</script>
<script>
const data=JSON.parse(document.getElementById('prediruta-data').textContent);
const safe=(value)=>String(value??'').replace(/[&<>\"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}}[c]));
const point=(place)=>place?{{lat:Number(place.lat),lng:Number(place.lng)}}:null;

async function initPrediRutaMap(){{
  const empty=document.getElementById('empty');
  try{{
  const [mapsLib,coreLib,markerLib,routesLib]=await Promise.all([
    google.maps.importLibrary('maps'),google.maps.importLibrary('core'),
    google.maps.importLibrary('marker'),google.maps.importLibrary('routes')
  ]);
  const {{Map,InfoWindow}}=mapsLib;
  const {{LatLngBounds}}=coreLib;
  const {{AdvancedMarkerElement,PinElement}}=markerLib;
  const {{Route}}=routesLib;
  const map=new Map(document.getElementById('map'),{{
    center:{{lat:4.6482,lng:-74.095}},zoom:11,mapTypeControl:false,
    fullscreenControl:true,streetViewControl:false,clickableIcons:false,
    gestureHandling:'cooperative',mapId:'DEMO_MAP_ID'
  }});
  const bounds=new LatLngBounds();
  const addPin=(position,label,color,title)=>{{
    bounds.extend(position);
    const pin=new PinElement({{background:color,borderColor:'#fff',
      glyph:label,glyphColor:'#fff',scale:1.05}});
    return new AdvancedMarkerElement({{map,position,title,content:pin.element}});
  }};

  if(data.mode==='preview'){{
    const origin=point(data.origin),destination=point(data.destination);
    if(origin)addPin(origin,'A','#14777a','Origen');
    if(destination)addPin(destination,'B','#17324d','Destino');
    if(origin&&destination){{
      empty.textContent='Calculando vista previa…';
      try{{
        const request={{origin,destination,travelMode:'DRIVING',fields:['path'],
          routingPreference:'TRAFFIC_AWARE',polylineQuality:'HIGH_QUALITY'}};
        if(data.departureTime)request.departureTime=new Date(data.departureTime);
        const result=await Route.computeRoutes(request);
        const route=result.routes?.[0];
        if(!route)throw new Error('Google no devolvió una ruta');
        route.createPolylines({{polylineOptions:{{strokeColor:'#168487',
          strokeOpacity:.92,strokeWeight:6}}}}).forEach(line=>line.setMap(map));
        (route.path||[]).forEach(p=>bounds.extend(p));
        empty.textContent='';
        if(!bounds.isEmpty())map.fitBounds(bounds,40);
      }}catch(error){{
        console.error('No fue posible dibujar la vista previa de la ruta.',error);
        empty.textContent='La ruta exacta se calculará al analizar.';
        map.fitBounds(bounds,65);
      }}
    }}else if(origin||destination){{
      empty.textContent='Selecciona el otro punto para completar tu trayecto.';
      map.setCenter(origin||destination);map.setZoom(15);
    }}else{{empty.textContent='Busca tu origen y destino para ver el recorrido en el mapa.';}}
    return;
  }}

  document.getElementById('legend').classList.add('show');
  const info=new InfoWindow();
  const tramos=data.tramos||[];
  const cantidadClima=Math.min(5,tramos.length);
  const puntosClima=new Set(Array.from({{length:cantidadClima}},(_,i)=>
    cantidadClima===1?0:Math.round(i*(tramos.length-1)/(cantidadClima-1))));
  tramos.forEach((tramo,index)=>{{
    const path=(tramo.puntos_polyline||[]).map(p=>({{lat:Number(p[0]),lng:Number(p[1])}}));
    if(!path.length)return;
    path.forEach(p=>bounds.extend(p));
    const puesto=Number(tramo.prioridad_recorrido)||null;
    const line=new google.maps.Polyline({{map,path,strokeColor:tramo.color,
      strokeOpacity:puesto ? 0.95 : 0.78,strokeWeight:puesto ? 8 : 6,
      zIndex:puesto ? 4 : 2}});
    if(index>0){{
      const divisor=document.createElement('div');divisor.className='segment-divider';
      new AdvancedMarkerElement({{map,position:path[0],content:divisor,zIndex:8,
        title:'Cambio de tramo'}});
    }}
    const clima=tramo.clima||{{}},estado=tramo.estado_actor;
    let estadoHtml='';
    if(estado?.probabilidades){{const p=estado.probabilidades;
      estadoHtml='<hr><b>Estado condicional si ocurre un siniestro</b><br>'+ 
        `Herido ${{(Number(p.HERIDO)*100).toFixed(0)}}% · Ileso ${{(Number(p.ILESO)*100).toFixed(0)}}% · Muerto ${{(Number(p.MUERTO)*100).toFixed(0)}}%`;}}
    line.addListener('click',event=>{{
      info.setContent(`<div style="font:13px Arial;line-height:1.55;max-width:310px;color:#263f4d">`+
        `<b>Tramo ${{safe(tramo.tramo)}} · Nivel ${{safe(tramo.nivel_criticidad)}}</b><br>`+
        `Hora estimada: ${{safe(tramo.hora_paso)}} · ${{safe(tramo.duracion)}}<br>`+
        `Clima: ${{safe(clima.condicion)}} · ${{Number(clima.temperatura).toFixed(1)}} °C<br>`+
        `Posibilidad de lluvia: ${{Number(clima.probabilidad_precipitacion).toFixed(0)}}%`+estadoHtml+
        '<hr><small>Comparación relativa con patrones históricos; no es una probabilidad individual.</small></div>');
      info.setPosition(event.latLng);info.open({{map}});
    }});
    if(puntosClima.has(index)){{
      const badge=document.createElement('div');badge.className='time-badge';
      badge.textContent=String(tramo.hora_paso||'').split(' - ')[0]+' · ☂ '+
        Number(clima.probabilidad_precipitacion).toFixed(0)+'%';
      new AdvancedMarkerElement({{map,position:path[Math.floor(path.length/2)],
        content:badge,zIndex:10,title:safe(clima.condicion)+' · posibilidad de lluvia'}});
    }}
  }});
  const start=point(data.start),end=point(data.end);
  if(start)addPin(start,'A','#14777a','Origen');
  if(end)addPin(end,'B','#17324d','Destino');
  if(!bounds.isEmpty())map.fitBounds(bounds,30);
  }}catch(error){{
    console.error('No fue posible iniciar el mapa de PrediRuta.',error);
    empty.innerHTML='<b>No pudimos cargar el mapa</b><br>'+safe(error?.message||
      'Google Maps no respondió correctamente.');
  }}
}}
window.gm_authFailure=()=>{{
  const mapNode=document.getElementById('map');
  mapNode.replaceChildren();
  mapNode.style.background='linear-gradient(145deg,#edf5f4,#dfeceb)';
  const empty=document.getElementById('empty');
  empty.innerHTML='<b>No pudimos autenticar Google Maps</b><br>'+ 
    'Revisa Maps JavaScript API, la facturación y los dominios permitidos de la clave.';
}};
</script>
<script async src="https://maps.googleapis.com/maps/api/js?key={clave_url}&v=weekly&language=es&region=CO&loading=async&callback=initPrediRutaMap"></script>
</body></html>"""


def mostrar_mapa_previo(
    api_key: str,
    origen: dict | None,
    destino: dict | None,
    salida: str,
    key: str,
) -> None:
    """Muestra origen, destino y una vista previa del recorrido."""

    if not api_key:
        st.info("Configura GOOGLE_MAPS_BROWSER_KEY para visualizar Google Maps.")
        return
    datos = {
        "mode": "preview",
        "origin": origen,
        "destination": destino,
        "departureTime": salida,
        "component": key,
    }
    components.html(_documento_mapa(api_key, datos), height=500, scrolling=False)


def mostrar_mapa_resultado(api_key: str, data: dict, key: str) -> None:
    """Dibuja cada tramo con su color, horario, clima y estado condicional."""

    if not api_key:
        st.info("Configura GOOGLE_MAPS_BROWSER_KEY para visualizar Google Maps.")
        return
    resumen = data["resumen"]
    inicio = resumen["start_location"]
    fin = resumen["end_location"]
    datos = {
        "mode": "result",
        "component": key,
        "start": {"lat": inicio["latitude"], "lng": inicio["longitude"]},
        "end": {"lat": fin["latitude"], "lng": fin["longitude"]},
        "tramos": data["tramos"],
    }
    components.html(_documento_mapa(api_key, datos), height=630, scrolling=False)
