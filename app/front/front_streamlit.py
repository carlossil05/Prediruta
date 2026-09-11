"""Interfaz visual de PrediRuta basada en los mockups de la entrega 1."""

from __future__ import annotations

import html
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import streamlit as st
from dotenv import load_dotenv

from google_maps_components import (
    mostrar_mapa_previo,
    mostrar_mapa_resultado,
    seleccionar_lugar,
)
from project_info import mostrar_informacion_proyecto


# En local se lee app/.env. En despliegue estas variables llegan del entorno.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/predict")
ENTORNO = os.getenv("APP_ENV", "local").lower()
PLACES_API_KEY = os.getenv("GOOGLE_PLACES_APIKEY", "")
MAPS_BROWSER_KEY = os.getenv("GOOGLE_MAPS_BROWSER_KEY", "")
if ENTORNO == "local":
    # En la prueba local una sola clave puede cubrir todos los servicios. Para
    # producción conviene separar la clave pública y restringirla por dominio.
    PLACES_API_KEY = PLACES_API_KEY or os.getenv("GOOGLE_APIKEY", "")
    MAPS_BROWSER_KEY = MAPS_BROWSER_KEY or os.getenv("GOOGLE_APIKEY", "")

ZONA_BOGOTA = ZoneInfo("America/Bogota")
DIAS_PRONOSTICO = 7

# Correspondencia exacta con DICCIONARIO_CATEGORIAS. Las etiquetas se adaptan
# al lenguaje del usuario, pero el modelo siempre recibe el código original.
GENEROS = {
    "Prefiero no decirlo": 0,  # SIN INFORMACION
    "Femenino": 1,
    "Masculino": 2,
}
CLASES_VEHICULO = {"Automóvil": 1, "Motocicleta": 13}
SERVICIOS_VEHICULO = {
    "Sin información": 0,
    "Diplomático": 1,
    "Oficial": 2,
    "Particular": 3,
    "Público": 4,
}


st.set_page_config(
    page_title="PrediRuta | Planea tu trayecto",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {--navy:#12324b;--teal:#14777a;--muted:#607581;--line:#dfe8e9;}
    html,body,[data-testid="stAppViewContainer"] {color-scheme:light;}
    .stApp {background:linear-gradient(180deg,#fcfefe 0%,#f5f9f8 100%);}
    header[data-testid="stHeader"] {background:rgba(252,254,254,.98);}
    [data-testid="stToolbar"] {color:var(--navy);}
    .block-container {max-width:1280px;padding:2.8rem 2rem 4rem;}
    #MainMenu,footer {visibility:hidden;}
    h1,h2,h3 {color:var(--navy);letter-spacing:-.025em;}
    .predi-brand {align-items:center;display:flex;gap:.7rem;margin-bottom:.15rem;}
    .predi-logo {align-items:center;background:linear-gradient(145deg,#16878a,#0f6467);
      border-radius:13px;color:#fff;display:flex;font-size:1.35rem;height:44px;
      justify-content:center;box-shadow:0 7px 18px rgba(20,119,122,.22);width:44px;}
    .predi-title {color:var(--navy);font-size:2rem;font-weight:800;letter-spacing:-.04em;}
    .predi-subtitle {color:var(--muted);font-size:1rem;margin:0 0 1.2rem 3.35rem;}
    .stepper {align-items:center;background:#fff;border:1px solid var(--line);
      border-radius:15px;display:grid;grid-template-columns:repeat(3,1fr);
      margin-bottom:1.25rem;padding:.72rem;box-shadow:0 8px 26px rgba(25,55,70,.04);}
    .step {align-items:center;color:#71838e;display:flex;font-size:.84rem;gap:.55rem;justify-content:center;}
    .step b {align-items:center;background:#e8f3f2;border-radius:50%;color:var(--teal);
      display:flex;height:27px;justify-content:center;width:27px;}
    .step.active {color:var(--navy);font-weight:750;}
    .panel-title {align-items:flex-start;display:flex;gap:.7rem;margin-bottom:.8rem;}
    .panel-icon {align-items:center;background:#e2f0ef;border-radius:50%;color:var(--teal);
      display:flex;flex:0 0 42px;font-size:1.2rem;height:42px;justify-content:center;}
    .panel-title strong {color:var(--navy);display:block;font-size:1.08rem;}
    .panel-title span {color:var(--muted);display:block;font-size:.82rem;margin-top:.14rem;}
    div[data-testid="stVerticalBlockBorderWrapper"] {background:#fff;
      border-color:var(--line)!important;border-radius:18px;
      box-shadow:0 12px 34px rgba(25,55,70,.055);}
    div[data-testid="stButton"] button[kind="primary"] {background:linear-gradient(90deg,#116f72,#16878a);
      border:0;border-radius:11px;box-shadow:0 7px 18px rgba(20,119,122,.2);
      min-height:48px;font-weight:750;}
    div[data-testid="stButton"] button[kind="primary"]:hover {background:#105f62;}
    .method-link {align-items:center;background:#fff;border:1px solid var(--line);
      border-radius:10px;color:var(--teal)!important;display:flex;font-size:.78rem;
      font-weight:750;justify-content:center;margin-top:.35rem;padding:.62rem .75rem;
      text-decoration:none!important;transition:.15s ease;}
    .method-link:hover {background:#eef7f6;border-color:#bcd8d6;}
    .privacy-line {color:#607783;font-size:.78rem;text-align:center;margin:.4rem 0 .2rem;}
    .route-strip {background:#fff;border:1px solid var(--line);border-radius:14px;
      display:grid;gap:.6rem;grid-template-columns:1.2fr 1.2fr .75fr;
      margin:.8rem 0 1.1rem;padding:.85rem 1rem;}
    .route-strip div {border-right:1px solid #e4eaed;color:#5d707c;font-size:.78rem;padding:0 .7rem;}
    .route-strip div:last-child {border-right:0;}
    .route-strip b {color:var(--navy);display:block;font-size:.9rem;margin-top:.17rem;}
    .metric-card {align-items:center;background:#fff;border:1px solid var(--line);
      border-radius:14px;display:grid;gap:.75rem;grid-template-columns:48px 1fr;
      margin-bottom:.7rem;padding:.75rem;box-shadow:0 7px 22px rgba(25,55,70,.045);}
    .metric-icon {align-items:center;background:#e8f4f3;border-radius:50%;color:var(--teal);
      display:flex;font-size:1.2rem;height:46px;justify-content:center;width:46px;}
    .metric-card.risk .metric-icon {background:#fff0ed;color:#cf4b3e;}
    .metric-label {color:#627580;font-size:.76rem;}.metric-value {color:var(--navy);
      font-size:1.12rem;font-weight:800;line-height:1.2;}.metric-note {color:#71838d;
      font-size:.73rem;margin-top:.1rem;}
    .notice {background:#eef4ff;border:1px solid #cad8f3;border-radius:12px;color:#465d78;
      font-size:.79rem;margin-top:1rem;padding:.75rem .85rem;}
    .journey-summary {background:#fff;border:1px solid var(--line);border-radius:16px;
      display:grid;grid-template-columns:1fr;gap:0;margin:.35rem 0 .7rem;
      box-shadow:0 8px 24px rgba(25,55,70,.045);overflow:hidden;}
    .summary-item {padding:.75rem .8rem;display:grid;grid-template-columns:34px 1fr;gap:.6rem;
      align-items:center;}.summary-item:first-child{border-bottom:1px solid var(--line)}
    .summary-icon {align-items:center;background:#e8f4f3;border-radius:50%;color:var(--teal);
      display:flex;height:34px;justify-content:center;width:34px;font-weight:800;}
    .summary-icon.alert {background:#fff0ed;color:#cf4b3e}.summary-label{color:#667b86;
      font-size:.7rem;font-weight:800;letter-spacing:.04em;text-transform:uppercase}
    .summary-value{color:var(--navy);font-size:.92rem;font-weight:800;margin-top:.12rem}
    .summary-note{color:#70818b;font-size:.73rem;margin-top:.1rem}
    .journey-list {background:#fff;border:1px solid var(--line);border-radius:16px;
      box-shadow:0 8px 24px rgba(25,55,70,.045);overflow:hidden;margin-bottom:.7rem;}
    .journey-head,.journey-row {display:grid;grid-template-columns:1.05fr .75fr 1.35fr .75fr .75fr;
      align-items:center;column-gap:.8rem;padding:.7rem 1rem;}
    .journey-head {background:#f4f8f8;color:#6a7e88;font-size:.67rem;font-weight:800;
      letter-spacing:.04em;text-transform:uppercase;}
    .journey-row {border-top:1px solid #e8eeee;min-height:58px;position:relative;}
    .journey-row::before {background:var(--segment-color);content:'';height:100%;left:0;
      position:absolute;top:0;width:5px;}.journey-row.high {background:#fff9f8;}
    .journey-step{align-items:center;display:flex;gap:.65rem}.journey-dot{align-items:center;
      background:var(--segment-color);border-radius:50%;color:#fff;display:flex;flex:0 0 28px;
      font-size:.69rem;font-weight:800;height:28px;justify-content:center;}
    .journey-time {color:var(--navy);font-size:.86rem;font-weight:800;line-height:1.2;}
    .journey-time small{color:#778993;display:block;font-size:.65rem;font-weight:600;margin-top:.15rem}
    .journey-weather {color:#3f5966;font-size:.78rem;line-height:1.3;}
    .rain-value{color:#176f82;font-size:.88rem;font-weight:850}.rain-value small{color:#71838d;
      display:block;font-size:.66rem;font-weight:600}.journey-duration{color:#425b68;font-size:.76rem;
      font-weight:700}.journey-duration small{color:#7b8b93;display:block;font-size:.65rem;font-weight:500}
    .journey-state {background:#fff3f0;border-top:1px dashed #efc8c0;color:#674a46;
      font-size:.72rem;grid-column:1/-1;margin:.55rem -1rem -.7rem;padding:.55rem 1rem .6rem 3.7rem;}
    .journey-state b{color:#a73d34}.journey-number {color:#657b86;font-size:.76rem;font-weight:700;}
    .priority-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.8rem;
      margin:.4rem 0 1.1rem}.priority-card{--card-color:#14777a;background:#fff;
      border:1px solid var(--line);border-top:5px solid var(--card-color);border-radius:14px;
      box-shadow:0 8px 24px rgba(25,55,70,.055);padding:.9rem;min-height:190px}
    .priority-card.detected{background:linear-gradient(180deg,#fff 0%,#fffaf8 100%)}
    .priority-card-top{align-items:center;display:flex;justify-content:space-between;gap:.5rem}
    .priority-rank{color:var(--card-color);font-size:.7rem;font-weight:850;letter-spacing:.04em;
      text-transform:uppercase}.priority-result{background:var(--card-color);border-radius:999px;
      color:#fff;font-size:.66rem;font-weight:800;padding:.2rem .48rem}
    .priority-route{color:var(--navy);font-size:.88rem;font-weight:800;line-height:1.35;
      margin:.7rem 0}.priority-route span{color:#7a8b94;font-size:.67rem;font-weight:700;
      text-transform:uppercase}.priority-meta{color:#536b77;font-size:.73rem;line-height:1.55}
    .priority-meta b{color:#294857}.state-block{border-top:1px dashed #e4c7c2;color:#6a4b47;
      font-size:.68rem;margin-top:.65rem;padding-top:.55rem}.state-title{color:#a33d35;
      font-weight:850;margin-bottom:.2rem}.state-values{display:flex;flex-wrap:wrap;gap:.45rem}
    .state-values b{color:#5a4140}
    .risk-pill {border-radius:999px;color:#fff;font-size:.7rem;font-weight:800;padding:.22rem .52rem;}
    .journey-time {color:var(--navy);font-size:1rem;font-weight:800;}
    .journey-weather {color:#425b68;font-size:.82rem;margin:.45rem 0;}
    .journey-note {color:#70818b;font-size:.73rem;line-height:1.35;}
    .section-copy {color:#607581;font-size:.88rem;margin-top:-.5rem;margin-bottom:1rem;}
    .method-box {background:#fff;border:1px solid var(--line);border-radius:14px;color:#506774;
      font-size:.82rem;line-height:1.6;margin-top:1.4rem;padding:1rem 1.1rem;}
    @media(max-width:800px){.block-container{padding:1rem}.predi-subtitle{margin-left:0}
      .step span{display:none}.route-strip{grid-template-columns:1fr}.route-strip div{
      border-right:0;border-bottom:1px solid #e4eaed;padding:.35rem}
      .priority-grid{grid-template-columns:1fr}
      .journey-head{display:none}.journey-row{
      grid-template-columns:1.15fr .75fr .85fr;row-gap:.55rem}.journey-step{grid-column:1/3}
      .journey-row>div:nth-child(2){grid-column:3;text-align:right}.journey-weather{
      grid-column:1;padding-left:0}.journey-duration{text-align:right}}
    </style>
    """,
    unsafe_allow_html=True,
)


def encabezado(titulo: str, subtitulo: str) -> None:
    st.markdown(
        f"""
        <div class="predi-brand"><div class="predi-logo">⌁</div>
        <div class="predi-title">{html.escape(titulo)}</div></div>
        <p class="predi-subtitle">{html.escape(subtitulo)}</p>
        """,
        unsafe_allow_html=True,
    )


def validar_formulario(
    origen: dict | None,
    destino: dict | None,
    salida: datetime,
    consentimiento: bool,
) -> list[str]:
    ahora = datetime.now(ZONA_BOGOTA)
    errores = []
    if not origen:
        errores.append("selecciona el origen desde las sugerencias")
    if not destino:
        errores.append("selecciona el destino desde las sugerencias")
    if origen and destino and origen.get("place_id") == destino.get("place_id"):
        errores.append("el origen y el destino deben ser diferentes")
    if salida < ahora + timedelta(minutes=5):
        errores.append("elige una salida al menos 5 minutos en el futuro")
    if not consentimiento:
        errores.append("confirma el uso temporal de los datos")
    if not PLACES_API_KEY:
        errores.append("configura la clave de Google Places")
    if not MAPS_BROWSER_KEY:
        errores.append("configura la clave de Google Maps del navegador")
    return errores


def solicitar_prediccion(payload: dict) -> dict | None:
    try:
        respuesta = requests.post(API_URL, json=payload, timeout=120)
    except requests.Timeout:
        st.error("El análisis tardó más de lo esperado. Intenta nuevamente.")
        return None
    except requests.RequestException:
        st.error("No pudimos conectar con PrediRuta. Comprueba que la API esté activa.")
        return None

    try:
        contenido = respuesta.json()
    except ValueError:
        contenido = {}
    if respuesta.ok:
        return contenido

    detalle = str(contenido.get("detail", "No fue posible completar la consulta."))
    if "are blocked" in detalle or "API_KEY_SERVICE_BLOCKED" in detalle:
        st.error(
            "La configuración de Google Maps del backend aún no está disponible. "
            "La pantalla podría estar conectada a una instancia anterior."
        )
        with st.expander("Información para soporte"):
            st.code(f"Backend: {API_URL}\n{detalle}")
    elif respuesta.status_code == 422 and "sale del área urbana" in detalle:
        st.error(
            "No podemos analizar este trayecto porque la ruta propuesta por Google "
            "sale de Bogotá. Prueba cambiar el origen, el destino o la hora de salida."
        )
    elif respuesta.status_code == 422:
        st.warning(detalle)
    elif respuesta.status_code == 502:
        st.error("No pudimos consultar Google en este momento. Intenta nuevamente.")
    else:
        st.error(detalle)
    return None


def tarjeta_metrica(icono: str, etiqueta: str, valor: str, nota: str, riesgo=False):
    clase = "metric-card risk" if riesgo else "metric-card"
    st.markdown(
        f"""
        <div class="{clase}"><div class="metric-icon">{icono}</div><div>
        <div class="metric-label">{html.escape(etiqueta)}</div>
        <div class="metric-value">{html.escape(valor)}</div>
        <div class="metric-note">{html.escape(nota)}</div></div></div>
        """,
        unsafe_allow_html=True,
    )


def nueva_consulta() -> None:
    st.session_state.resultado = None
    st.session_state.consulta = None
    for clave in ("lugar_origen", "lugar_destino"):
        st.session_state.pop(clave, None)


def mostrar_planeacion() -> None:
    columna_encabezado, columna_metodologia = st.columns([4.5, 1.25])
    with columna_encabezado:
        encabezado(
            "PrediRuta | Planea tu trayecto",
            "Compara tu recorrido con patrones históricos de siniestros y revisa el clima previsto.",
        )
    with columna_metodologia:
        st.markdown(
            '<a class="method-link" href="?vista=proyecto" target="_self" '
            'title="Metodología, modelos, resultados y limitaciones">'
            "Conoce el proyecto →</a>",
            unsafe_allow_html=True,
        )
    st.markdown(
        """
        <div class="stepper">
          <div class="step active"><b>1</b><span>Selecciona tu ruta</span></div>
          <div class="step active"><b>2</b><span>Completa el contexto</span></div>
          <div class="step"><b>3</b><span>Revisa el análisis</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    ahora = datetime.now(ZONA_BOGOTA).replace(second=0, microsecond=0)
    salida_inicial = ahora + timedelta(minutes=15)
    fecha_maxima = ahora.date() + timedelta(days=DIAS_PRONOSTICO - 1)
    columna_formulario, columna_mapa = st.columns([0.92, 1.28], gap="large")

    with columna_formulario:
        with st.container(border=True):
            st.markdown(
                """
                <div class="panel-title"><div class="panel-icon">⌁</div><div>
                <strong>Define tu ruta</strong>
                <span>Escribe y selecciona lugares reales de Google.</span>
                </div></div>
                """,
                unsafe_allow_html=True,
            )
            origen = seleccionar_lugar(
                PLACES_API_KEY, "Punto de origen", "Ej. Portal Norte, Bogotá",
                "origin", "lugar_origen",
            )
            destino = seleccionar_lugar(
                PLACES_API_KEY, "Punto de destino",
                "Ej. Universidad de los Andes, Bogotá", "destination",
                "lugar_destino",
            )
            st.caption(
                "Cobertura: solo ubicaciones del área urbana de Bogotá "
                "incluida en las zonas de entrenamiento."
            )

            columna_fecha, columna_hora = st.columns(2)
            with columna_fecha:
                fecha_salida = st.date_input(
                    "Fecha", value=salida_inicial.date(), min_value=ahora.date(),
                    max_value=fecha_maxima,
                    help="Puedes consultar hoy y los próximos seis días.",
                )
            with columna_hora:
                hora_salida = st.time_input(
                    "Hora de salida", value=salida_inicial.time(), step=300,
                    help="Google usa esta hora para estimar el tráfico.",
                )

            st.markdown("#### Información para personalizar el análisis")
            st.caption(
                "No modifica el nivel del recorrido. Solo alimenta el análisis "
                "complementario de estado cuando la similitud histórica es mayor."
            )
            edad = st.number_input("Edad", min_value=0, max_value=110, value=35)
            columna_genero, columna_vehiculo = st.columns(2)
            with columna_genero:
                genero_texto = st.selectbox("Género", list(GENEROS), index=0)
            with columna_vehiculo:
                clase_texto = st.selectbox(
                    "Vehículo", list(CLASES_VEHICULO), index=0
                )
            servicio_texto = st.selectbox(
                "Servicio del vehículo", list(SERVICIOS_VEHICULO), index=3
            )
            consentimiento = st.checkbox(
                "Entiendo que estos datos se usarán únicamente para esta consulta "
                "de PrediRuta y no serán almacenados ni usados para otro fin."
            )
            st.markdown(
                '<div class="privacy-line">🔒 Uso temporal · sin almacenamiento del perfil</div>',
                unsafe_allow_html=True,
            )

            salida = datetime.combine(fecha_salida, hora_salida, tzinfo=ZONA_BOGOTA)
            errores = validar_formulario(origen, destino, salida, consentimiento)
            if errores:
                st.caption("Para continuar: " + "; ".join(errores) + ".")
            analizar = st.button(
                "Analizar mi trayecto  →", type="primary", width="stretch",
                disabled=bool(errores),
            )

    with columna_mapa:
        st.markdown(
            """
            <div class="panel-title"><div class="panel-icon">⌁</div><div>
            <strong>Confirma visualmente tu trayecto</strong>
            <span>La vista previa se actualiza al elegir origen y destino.</span>
            </div></div>
            """,
            unsafe_allow_html=True,
        )
        mostrar_mapa_previo(
            MAPS_BROWSER_KEY, origen, destino, salida.isoformat(), "mapa_planeacion"
        )
        st.caption(
            "Antes de procesar verificamos todos los puntos. Si Google propone "
            "salir de Bogotá, te lo informaremos y no ejecutaremos los modelos."
        )

    if analizar:
        payload = {
            "origen": origen["address"],
            "destino": destino["address"],
            "origen_coordenadas": {
                "latitud": origen["lat"], "longitud": origen["lng"]
            },
            "destino_coordenadas": {
                "latitud": destino["lat"], "longitud": destino["lng"]
            },
            "fecha_salida": fecha_salida.isoformat(),
            "hora_salida": hora_salida.strftime("%H:%M"),
            "perfil_actor": {
                "edad": int(edad), "genero": GENEROS[genero_texto],
                "clase_vehiculo": CLASES_VEHICULO[clase_texto],
                "servicio_vehiculo": SERVICIOS_VEHICULO[servicio_texto],
            },
            "consentimiento_datos": consentimiento,
        }
        with st.spinner("Analizando la ruta, el tráfico y el clima de cada tramo…"):
            resultado = solicitar_prediccion(payload)
        if resultado:
            st.session_state.resultado = resultado
            st.session_state.consulta = {
                "origen": origen["name"] or origen["address"],
                "destino": destino["name"] or destino["address"],
                "salida": salida.isoformat(),
            }
            st.rerun()


def fila_tramo(tramo: dict) -> str:
    """Presenta un tramo como una fila comparable dentro del recorrido."""

    clima = tramo["clima"]
    if tramo.get("prioridad_recorrido"):
        resultado_modelo = f"#{tramo['prioridad_recorrido']} detectado"
    elif tramo.get("patron_detectado"):
        resultado_modelo = "Detectado"
    else:
        resultado_modelo = "No detectado"
    distancia = tramo.get("distancia_metros", 0)
    distancia_texto = (
        f"{distancia / 1000:.1f} km" if distancia >= 1000 else f"{distancia:.0f} m"
    )
    estado = tramo.get("estado_actor")
    estado_html = ""
    if estado:
        probabilidades = estado["probabilidades"]
        estado_html = (
            '<div class="journey-state"><b>Si ocurriera un siniestro:</b> '
            f"herido {probabilidades['HERIDO']:.0%} · "
            f"ileso {probabilidades['ILESO']:.0%} · "
            f"muerto {probabilidades['MUERTO']:.0%}. "
            "Esta estimación no indica que vaya a ocurrir.</div>"
        )
    clase_alta = " high" if tramo["nivel_criticidad"] == "Alto" else ""
    hora_paso = hora_paso_legible(tramo)
    return (
        f'<div class="journey-row{clase_alta}" style="--segment-color:{tramo["color"]}">'
        f'<div class="journey-step"><span class="journey-dot">{tramo["tramo"]}</span>'
        f'<div class="journey-time">{html.escape(hora_paso)}'
        '<small>hora de paso estimada</small></div></div>'
        f'<div><span class="risk-pill" style="background:{tramo["color"]}">'
        f'{html.escape(resultado_modelo)}</span></div>'
        f'<div class="journey-weather">☁ {html.escape(clima["condicion"])}<br>'
        f'{clima["temperatura"]:.1f} °C</div>'
        f'<div class="rain-value">☂ {clima["probabilidad_precipitacion"]:.0f}%'
        '<small>prob. de lluvia</small></div>'
        f'<div class="journey-duration">{html.escape(tramo["duracion"])}'
        f'<small>{distancia_texto}</small></div>{estado_html}</div>'
    )


def hora_paso_legible(tramo: dict) -> str:
    """Evita rangos engañosos como ``10:00 - 10:00`` en tramos muy cortos."""

    hora_paso = str(tramo.get("hora_paso", ""))
    inicio, separador, fin = hora_paso.partition(" - ")
    if separador and inicio == fin:
        return f"{inicio} aprox."
    return hora_paso


def lista_tramos(tramos: list[dict]) -> str:
    """Construye una única secuencia visual para facilitar comparaciones."""

    filas = "".join(fila_tramo(tramo) for tramo in tramos)
    return (
        '<div class="journey-list"><div class="journey-head">'
        '<span>Tramo y hora</span><span>Resultado del modelo</span>'
        '<span>Condición</span><span>Lluvia</span><span>Tiempo · distancia</span>'
        f"</div>{filas}</div>"
    )


def tarjeta_tramo_prioritario(tramo: dict) -> str:
    """Resume uno de los cinco scores más altos con referencias espaciales."""

    clima = tramo["clima"]
    ubicacion = tramo.get("ubicacion_sector") or {}
    desde = ubicacion.get("desde", "Inicio del tramo")
    hasta = ubicacion.get("hasta", "Fin del tramo")
    detectado = bool(tramo.get("patron_detectado"))
    resultado = "Patrón detectado" if detectado else "No detectado"
    clase = " detected" if detectado else ""
    distancia = tramo.get("distancia_metros", 0)
    distancia_texto = (
        f"{distancia / 1000:.1f} km" if distancia >= 1000 else f"{distancia:.0f} m"
    )
    estado_html = ""
    if tramo.get("estado_actor"):
        probabilidades = tramo["estado_actor"]["probabilidades"]
        estado_mas_probable = tramo["estado_actor"]["estado_mas_probable"].capitalize()
        estado_html = (
            '<div class="state-block"><div class="state-title">'
            "Si ocurriera un siniestro · resultado más probable: "
            f"{html.escape(estado_mas_probable)}</div>"
            '<div class="state-values">'
            f"<span><b>Herido</b> {probabilidades['HERIDO']:.0%}</span>"
            f"<span><b>Ileso</b> {probabilidades['ILESO']:.0%}</span>"
            f"<span><b>Muerto</b> {probabilidades['MUERTO']:.0%}</span>"
            "</div></div>"
        )
    hora_paso = hora_paso_legible(tramo)
    return (
        f'<div class="priority-card{clase}" style="--card-color:{tramo["color"]}">'
        '<div class="priority-card-top">'
        f'<span class="priority-rank">#{tramo["ranking_recorrido"]} mayor score</span>'
        f'<span class="priority-result">{resultado}</span></div>'
        '<div class="priority-route"><span>Desde</span><br>'
        f'{html.escape(desde)}<br><span>Hasta</span><br>{html.escape(hasta)}</div>'
        f'<div class="priority-meta"><b>◷ {html.escape(hora_paso)}</b> · '
        f'{html.escape(tramo["duracion"])} · {distancia_texto}<br>'
        f'☁ {html.escape(clima["condicion"])} · {clima["temperatura"]:.1f} °C · '
        f'<b>☂ {clima["probabilidad_precipitacion"]:.0f}% lluvia</b></div>'
        f"{estado_html}</div>"
    )


def mostrar_resultado() -> None:
    data = st.session_state.resultado
    consulta = st.session_state.consulta or {}
    resumen = data["resumen"]
    columna_titulo, columna_accion = st.columns([5, 1])
    with columna_titulo:
        encabezado(
            "PrediRuta | Condiciones de tu recorrido",
            "Identifica dónde el modelo detecta patrones de ocurrencia y revisa el clima previsto.",
        )
    with columna_accion:
        st.button("← Nueva consulta", on_click=nueva_consulta, width="stretch")

    salida = datetime.fromisoformat(consulta.get("salida", resumen["hora_llegada"]))
    st.markdown(
        f"""
        <div class="route-strip">
          <div>● Desde<b>{html.escape(consulta.get('origen','Origen'))}</b></div>
          <div>◆ Hasta<b>{html.escape(consulta.get('destino','Destino'))}</b></div>
          <div>◷ Salida<b>{salida:%d/%m · %H:%M}</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tramos = data["tramos"]
    tramos_altos = [tramo for tramo in tramos if tramo["nivel_criticidad"] == "Alto"]
    tramo_lluvia = max(
        tramos, key=lambda tramo: tramo["clima"]["probabilidad_precipitacion"]
    )
    patrones_detectados = resumen.get(
        "patrones_detectados",
        sum(tramo.get("patron_detectado", False) for tramo in tramos),
    )
    if patrones_detectados:
        horas_atencion = ", ".join(
            tramo["hora_paso"].split(" - ")[0] for tramo in tramos_altos[:3]
        )
        lectura_riesgo = f"Coincidencias en {patrones_detectados} tramo(s)"
        nota_riesgo = (
            f"En rojo aparecen los {len(tramos_altos)} scores mayores"
            + (f": {horas_atencion}" if horas_atencion else "")
        )
    else:
        lectura_riesgo = "Sin coincidencias sobre el umbral"
        nota_riesgo = "Ningún tramo superó el umbral validado"

    llegada = datetime.fromisoformat(resumen["hora_llegada"])
    columna_mapa, columna_metricas = st.columns([2.15, .92], gap="large")
    with columna_mapa:
        mostrar_mapa_resultado(MAPS_BROWSER_KEY, data, "mapa_resultado")
        st.caption(
            "El color resume el nivel relativo y los puntos blancos separan los tramos. "
            "Las etiquetas muestran hora y posibilidad de lluvia. Haz clic sobre cualquier "
            "sección de la ruta para consultar su información completa."
        )
    with columna_metricas:
        tarjeta_metrica("◷", "Tiempo estimado", resumen["duracion_estimada"],
                        f"Llegada aproximada: {llegada:%H:%M}")
        tarjeta_metrica("⌁", "Distancia", f"{resumen['distancia_total_km']:.1f} km",
                        f"{resumen['total_tramos']} tramos analizados")
        st.markdown("#### Lo más importante")
        st.markdown(
            f'<div class="journey-summary"><div class="summary-item">'
            '<div class="summary-icon alert">!</div><div>'
            '<div class="summary-label">Resultado del modelo de ocurrencia</div>'
            f'<div class="summary-value">{html.escape(lectura_riesgo)}</div>'
            f'<div class="summary-note">{html.escape(nota_riesgo)}</div></div></div>'
            '<div class="summary-item"><div class="summary-icon">☂</div><div>'
            '<div class="summary-label">Mayor posibilidad de lluvia</div>'
            f'<div class="summary-value">{tramo_lluvia["clima"]["probabilidad_precipitacion"]:.0f}% · '
            f'{html.escape(tramo_lluvia["clima"]["condicion"])}</div>'
            f'<div class="summary-note">Tramo {tramo_lluvia["tramo"]} · '
            f'{html.escape(tramo_lluvia["hora_paso"])}</div></div></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="notice"><b>Ten en cuenta</b><br>Los tiempos pueden cambiar
            con el tráfico y el pronóstico. “Detectado” significa que el score superó
            el umbral validado del modelo; no representa tu probabilidad de accidente.</div>
            """,
            unsafe_allow_html=True,
        )

    cinco_criticos = sorted(
        (tramo for tramo in tramos if tramo.get("ranking_recorrido")),
        key=lambda tramo: tramo["ranking_recorrido"],
    )
    st.markdown("### Los cinco tramos con mayor score")
    st.markdown(
        '<p class="section-copy">Se ordenan comparativamente dentro de esta ruta. '
        '“Patrón detectado” significa que el resultado superó el umbral validado; '
        'el ranking no es una probabilidad de accidente.</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="priority-grid">'
        + "".join(tarjeta_tramo_prioritario(tramo) for tramo in cinco_criticos)
        + "</div>",
        unsafe_allow_html=True,
    )

    with st.expander(f"Consultar el detalle de los {len(tramos)} tramos"):
        st.caption(
            "El mapa prioriza hasta tres scores que superaron el umbral. Esta tabla conserva todos "
            "los tramos, en el orden exacto del recorrido, para una revisión detallada."
        )
        st.markdown(lista_tramos(tramos), unsafe_allow_html=True)

    with st.expander("¿Cómo construimos este análisis?"):
        st.markdown(
            f"""
            1. **Ruta y tiempos:** {resumen['fuente_tiempos']} calcula la ruta y
               una duración para cada cambio entre clusters.
            2. **Clima:** {resumen['fuente_clima']} consulta el punto y la hora
               representativos de cada tramo.
            3. **Modelo de ocurrencia:** recibe zona, mes, día, hora, temperatura,
               precipitación, nubosidad, presión y viento. “Detectado” indica que
               el score superó el umbral validado; no es una probabilidad individual.
            4. **Privacidad:** los datos adicionales se procesan temporalmente y
               PrediRuta no implementa su almacenamiento.
            """
        )
        st.markdown(
            '<a class="method-link" href="?vista=proyecto" target="_self">'
            "Conoce la metodología, los experimentos y sus resultados →</a>",
            unsafe_allow_html=True,
        )


st.session_state.setdefault("resultado", None)
st.session_state.setdefault("consulta", None)

# Descarta resultados generados antes de incorporar explícitamente el umbral y
# la clasificación del modelo; evita mezclar semánticas en una misma sesión.
if st.session_state.resultado and any(
    "patron_detectado" not in tramo
    for tramo in st.session_state.resultado.get("tramos", [])
):
    st.session_state.resultado = None
    st.session_state.consulta = None

if st.query_params.get("vista") == "proyecto":
    mostrar_informacion_proyecto()
elif st.session_state.resultado:
    mostrar_resultado()
else:
    mostrar_planeacion()
