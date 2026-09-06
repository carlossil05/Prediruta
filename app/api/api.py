import os
import math
import joblib
import requests
import googlemaps
import polyline
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Inicialización de FastAPI
app = FastAPI(
    title="API PrediRuta - Riesgo Vial Bogotá (MLP)",
    version="3.0.0",
    description="API centralizada con modelo MLP (11 variables) para inferencia de riesgo vial."
)

# Carga de Variables y Artefactos
GOOGLE_APIKEY = os.getenv("GOOGLE_APIKEY")
# Actualizado al nuevo nombre del modelo
MODEL_PATH = os.path.join("modelo", "modelo_ocurrencia_temporal.joblib")
CENTROIDES_PATH = os.path.join("modelo", "centroides_zonas.csv")

if not os.path.exists(MODEL_PATH) or not os.path.exists(CENTROIDES_PATH):
    raise FileNotFoundError(f"Faltan archivos en 'modelo/'. Verifica que existan {MODEL_PATH} y {CENTROIDES_PATH}")

# El Pipeline de Scikit-Learn (ya incluye escalado y one-hot encoding internamente)
model = joblib.load(MODEL_PATH)
centroides_df = pd.read_csv(CENTROIDES_PATH)

LATS_CENTROIDES = centroides_df['LATITUD_CENTROIDE'].values
LNGS_CENTROIDES = centroides_df['LONGITUD_CENTROIDE'].values
ZONAS_IDS = centroides_df['ZONA_CIUDAD'].values

#Se calcula como el diametro de los clusters: raiz(AreaBogota/Nclusters)*2=raiz(384/150)*2=3.2
DISTANCIA_TRAMO_KM = 3.2

# --- FUNCIONES GEOGRÁFICAS Y METEOROLÓGICAS ---

def obtener_zona_mas_cercana(lat_punto: float, lng_punto: float) -> int:
    distancias = (LATS_CENTROIDES - lat_punto)**2 + (LNGS_CENTROIDES - lng_punto)**2
    indice_minimo = np.argmin(distancias)
    return int(ZONAS_IDS[indice_minimo])

def haversine_distance(coord1, coord2):
    R = 6371.0
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def interpolar_punto(p1, p2, fraccion):
    return (p1[0] + (p2[0] - p1[0]) * fraccion, p1[1] + (p2[1] - p1[1]) * fraccion)

def segmentar_ruta(puntos_full, tamano_tramo_km):
    if not puntos_full or len(puntos_full) < 2:
        return [puntos_full] if puntos_full else []

    tramos, tramo_actual, dist_acumulada = [], [puntos_full[0]], 0.0

    for i in range(len(puntos_full) - 1):
        p_inicio, p_fin = puntos_full[i], puntos_full[i+1]
        dist_segmento = haversine_distance(p_inicio, p_fin)
        if dist_segmento == 0:
            continue

        p_cursor, dist_restante = p_inicio, dist_segmento

        while dist_acumulada + dist_restante >= tamano_tramo_km:
            necesario = tamano_tramo_km - dist_acumulada
            p_corte = interpolar_punto(p_cursor, p_fin, necesario / dist_restante)
            tramo_actual.append(p_corte)
            tramos.append(tramo_actual)
            tramo_actual, dist_acumulada, p_cursor = [p_corte], 0.0, p_corte
            dist_restante = haversine_distance(p_cursor, p_fin)

        if dist_restante > 0:
            tramo_actual.append(p_fin)
            dist_acumulada += dist_restante

    if len(tramo_actual) > 1:
        tramos.append(tramo_actual)

    return tramos

def obtener_clima_tramo(lat, lng, hora_paso):
    """
    Obtiene las 6 variables climáticas base y calcula las 2 trigonométricas
    requeridas por el nuevo modelo MLP.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat, "longitude": lng,
            # Se solicitan todas las variables necesarias para el modelo
            "hourly": "temperature_2m,precipitation,cloud_cover,surface_pressure,wind_speed_10m,wind_direction_10m",
            "forecast_days": 1, "timezone": "America/Bogota"
        }
        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        if "hourly" in data:
            hora_str = hora_paso.strftime("%Y-%m-%dT%H:00")
            idx = data["hourly"]["time"].index(hora_str) if hora_str in data["hourly"]["time"] else 0
            
            temp = data["hourly"]["temperature_2m"][idx]
            precip = data["hourly"]["precipitation"][idx]
            nubosidad = data["hourly"]["cloud_cover"][idx]
            presion = data["hourly"]["surface_pressure"][idx]
            v_viento = data["hourly"]["wind_speed_10m"][idx]
            dir_viento_grados = data["hourly"]["wind_direction_10m"][idx]

            # Transformaciones trigonométricas para la dirección del viento
            dir_sin = math.sin(math.radians(dir_viento_grados))
            dir_cos = math.cos(math.radians(dir_viento_grados))

            return temp, precip, nubosidad, presion, v_viento, dir_sin, dir_cos

    except Exception:
        pass
    
    # Fallback con valores promedio si la API falla
    return 15.0, 0.0, 50.0, 750.0, 10.0, 0.0, 1.0

# --- ESQUEMAS DE ENTRADA Y SALIDA ---

class SolicitudRuta(BaseModel):
    origen: str = Field(..., example="Universidad Nacional de Colombia, Bogotá")
    destino: str = Field(..., example="Parque de la 93, Bogotá")
    fecha_salida: str = Field(..., example="2026-10-25")  # NUEVO CAMPO
    hora_salida: str = Field(..., example="14:30")


UMBRAL_BAJO, UMBRAL_MEDIO = 0.3, 0.6

def clasificar_riesgo(prob: float):
    if prob < UMBRAL_BAJO:
        return {"nivel": "Bajo", "color": "green"}
    elif prob < UMBRAL_MEDIO:
        return {"nivel": "Medio", "color": "orange"}
    return {"nivel": "Alto", "color": "red"}

# --- ENDPOINTS ---

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API PrediRuta operativa (MLP Pipeline)"}

@app.post("/predict")
def procesar_y_predecir_ruta(data: SolicitudRuta):
    if not GOOGLE_APIKEY:
        raise HTTPException(status_code=500, detail="GOOGLE_APIKEY no configurada.")

    try:
        fecha_dt = datetime.strptime(data.fecha_salida, "%Y-%m-%d").date()
        hora_dt = datetime.strptime(data.hora_salida, "%H:%M").time()
        departure_time = datetime.combine(fecha_dt, hora_dt)

        gmaps = googlemaps.Client(key=GOOGLE_APIKEY)
        directions = gmaps.directions(data.origen, data.destino, mode="driving", departure_time=departure_time)

        if not directions:
            raise HTTPException(status_code=404, detail="No se encontró una ruta válida.")

        leg = directions[0]['legs'][0]
        points_decoded = polyline.decode(directions[0]['overview_polyline']['points'])

        tramos_segmentados = segmentar_ruta(points_decoded, DISTANCIA_TRAMO_KM)
        duracion_seg = leg['duration']['value']
        seg_por_tramo = duracion_seg / len(tramos_segmentados) if tramos_segmentados else 0

        registros = []
        hora_acumulada = departure_time

        for idx, tramo_pts in enumerate(tramos_segmentados):
            h_inicio = hora_acumulada
            h_fin = hora_acumulada + timedelta(seconds=seg_por_tramo)
            hora_acumulada = h_fin

            lat_in, lng_in = tramo_pts[0]
            lat_out, lng_out = tramo_pts[-1]

            # Consulta expandida para el MLP
            temp, precip, nubosidad, presion, v_viento, dir_sin, dir_cos = obtener_clima_tramo(lat_in, lng_in, h_inicio)
            zona = obtener_zona_mas_cercana(lat_in, lng_in)

            registros.append({
                "tramo": idx + 1,
                "puntos_polyline": tramo_pts,
                "hora_paso": f"{h_inicio.strftime('%H:%M')} - {h_fin.strftime('%H:%M')}",
                "origen_coord": f"{lat_in:.4f}, {lng_in:.4f}",
                "destino_coord": f"{lat_out:.4f}, {lng_out:.4f}",
                # Columnas exactas requeridas por el modelo
                "ZONA_CIUDAD": zona,
                "MES": h_inicio.month,
                "DIA_SEMANA": h_inicio.weekday(),
                "HORA": h_inicio.hour,
                "TEMPERATURA_2M": temp,
                "PRECIPITACION": precip,
                "NUBOSIDAD": nubosidad,
                "PRESION_SUPERFICIE": presion,
                "VELOCIDAD_VIENTO_10M": v_viento,
                "DIRECCION_VIENTO_10M_SIN": dir_sin,
                "DIRECCION_VIENTO_10M_COS": dir_cos
            })

        df_input = pd.DataFrame(registros)

        # Orden estricto de las 11 columnas
        columnas_modelo = [
            'ZONA_CIUDAD', 'MES', 'DIA_SEMANA', 'HORA', 
            'TEMPERATURA_2M', 'PRECIPITACION', 'NUBOSIDAD', 
            'PRESION_SUPERFICIE', 'VELOCIDAD_VIENTO_10M', 
            'DIRECCION_VIENTO_10M_SIN', 'DIRECCION_VIENTO_10M_COS'
        ]
        
        # El pipeline de sklearn se encarga internamente de escalar e imputar
        probabilidades = model.predict_proba(df_input[columnas_modelo])[:, 1]

        detalle_tramos = []
        for idx, row in df_input.iterrows():
            prob = float(probabilidades[idx])
            riesgo = clasificar_riesgo(prob)

            detalle_tramos.append({
                "tramo": int(row['tramo']),
                "puntos_polyline": row['puntos_polyline'],
                "hora_paso": row['hora_paso'],
                "origen_coord": row['origen_coord'],
                "destino_coord": row['destino_coord'],
                "clima": {
                    "temperatura": row['TEMPERATURA_2M'],
                    "lluvia": row['PRECIPITACION'],
                    "viento": row['VELOCIDAD_VIENTO_10M']
                },
                "probabilidad": round(prob, 4),
                "nivel_riesgo": riesgo["nivel"],
                "color": riesgo["color"]
            })

        return {
            "resumen": {
                "distancia_total": leg['distance']['text'],
                "duracion_estimada": leg['duration']['text'],
                "total_tramos": len(detalle_tramos),
                "riesgo_maximo_ruta": max([t["probabilidad"] for t in detalle_tramos]) if detalle_tramos else 0.0,
                "start_location": leg['start_location'],
                "end_location": leg['end_location']
            },
            "tramos": detalle_tramos
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar la ruta: {str(e)}")