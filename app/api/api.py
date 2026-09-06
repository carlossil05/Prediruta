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
from typing import List, Optional

# Inicialización de FastAPI
app = FastAPI(
    title="API PrediRuta - Riesgo Vial Bogotá",
    version="2.0.0",
    description="API centralizada para cálculo de rutas, segmentación, clima e inferencia de riesgo vial."
)

# Carga de Variables y Artefactos
GOOGLE_APIKEY = os.getenv("GOOGLE_APIKEY")
MODEL_PATH = os.path.join("modelo", "modelo_xgboost_bogota.joblib")
CENTROIDES_PATH = os.path.join("modelo", "centroides_zonas.csv")

if not os.path.exists(MODEL_PATH) or not os.path.exists(CENTROIDES_PATH):
    raise FileNotFoundError("Los archivos 'modelo_xgboost_bogota.joblib' y 'centroides_zonas.csv' no están en el directorio 'modelo/'.")

model = joblib.load(MODEL_PATH)
centroides_df = pd.read_csv(CENTROIDES_PATH)

LATS_CENTROIDES = centroides_df['LATITUD_CENTROIDE'].values
LNGS_CENTROIDES = centroides_df['LONGITUD_CENTROIDE'].values
ZONAS_IDS = centroides_df['ZONA_CIUDAD'].values

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

def obtener_clima_tramo(lat: float, lng: float, hora_paso):
    """
    Consulta el clima para las coordenadas dadas utilizando la Google Weather API.
    """
    if not GOOGLE_APIKEY:
        return 18.0, 0.0, 10.0  # Fallback si no hay API key

    try:
        # Endpoint oficial de pronóstico por horas de Google Weather API
        url = "https://weather.googleapis.com/v1/forecast/hourly:lookup"
        params = {
            "key": GOOGLE_APIKEY,
            "location.latitude": lat,
            "location.longitude": lng,
            "hours": 24
        }
        res = requests.get(url, params=params, timeout=5)
        
        if res.status_code == 200:
            data = res.json()
            
            # Extraer las variables requeridas para tu modelo XGBoost
            # (Sensación térmica, Lluvia/Precipitación, Velocidad del viento)
            forecast = data.get("hourlyForecasts", [])[0]
            
            sensacion_termica = forecast.get("feelsLikeTemperature", {}).get("value", 18.0)
            lluvia = forecast.get("precipitation", {}).get("qpfQuantity", {}).get("value", 0.0)
            viento = forecast.get("wind", {}).get("speed", {}).get("value", 10.0)

            return sensacion_termica, lluvia, viento

    except Exception:
        pass

    # Valores por defecto en caso de fallo en la llamada HTTP
    return 18.0, 0.0, 10.0

# --- ESQUEMAS DE ENTRADA Y SALIDA ---

class SolicitudRuta(BaseModel):
    origen: str = Field(..., example="Universidad Nacional de Colombia, Bogotá")
    destino: str = Field(..., example="Parque de la 93, Bogotá")
    hora_salida: str = Field(..., example="14:30")  # Formato HH:MM
    distancia_tramo_km: float = Field(1.0, ge=0.1, le=10.0, example=1.0)

# Clasificación de Riesgo
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
    return {"status": "ok", "message": "API PrediRuta operativa (v2.0.0)"}

@app.post("/predict")
def procesar_y_predecir_ruta(data: SolicitudRuta):
    if not GOOGLE_APIKEY:
        raise HTTPException(status_code=500, detail="GOOGLE_APIKEY no configurada en el servidor backend.")

    try:
        # 1. Parsing de fecha y hora
        hoy = datetime.now().date()
        hora_dt = datetime.strptime(data.hora_salida, "%H:%M").time()
        departure_time = datetime.combine(hoy, hora_dt)

        # 2. Consulta a Google Maps
        gmaps = googlemaps.Client(key=GOOGLE_APIKEY)
        directions = gmaps.directions(data.origen, data.destino, mode="driving", departure_time=departure_time)

        if not directions:
            raise HTTPException(status_code=404, detail="No se encontró una ruta válida para las direcciones especificadas.")

        leg = directions[0]['legs'][0]
        points_decoded = polyline.decode(directions[0]['overview_polyline']['points'])

        # 3. Segmentación de ruta
        tramos_segmentados = segmentar_ruta(points_decoded, data.distancia_tramo_km)
        duracion_seg = leg['duration']['value']
        seg_por_tramo = duracion_seg / len(tramos_segmentados) if tramos_segmentados else 0

        # 4. Construcción de Dataset para Inferencia
        registros = []
        hora_acumulada = departure_time

        for idx, tramo_pts in enumerate(tramos_segmentados):
            h_inicio = hora_acumulada
            h_fin = hora_acumulada + timedelta(seconds=seg_por_tramo)
            hora_acumulada = h_fin

            lat_in, lng_in = tramo_pts[0]
            lat_out, lng_out = tramo_pts[-1]

            sens, lluvia, viento = obtener_clima_tramo(lat_in, lng_in, h_inicio)
            zona = obtener_zona_mas_cercana(lat_in, lng_in)

            registros.append({
                "tramo": idx + 1,
                "puntos_polyline": tramo_pts,
                "hora_inicio": h_inicio.strftime("%H:%M"),
                "hora_fin": h_fin.strftime("%H:%M"),
                "lat_inicio": lat_in,
                "lng_inicio": lng_in,
                "lat_fin": lat_out,
                "lng_fin": lng_out,
                "ZONA_CIUDAD": zona,
                "MES": h_inicio.month,
                "DIA_SEMANA": h_inicio.weekday(),
                "HORA": h_inicio.hour,
                "SENSACION_TERMICA": sens,
                "LLUVIA": lluvia,
                "VELOCIDAD_VIENTO_10M": viento
            })

        df_input = pd.DataFrame(registros)

        # 5. Predicción Vectorizada con XGBoost
        columnas_modelo = ['ZONA_CIUDAD', 'MES', 'DIA_SEMANA', 'HORA', 'SENSACION_TERMICA', 'LLUVIA', 'VELOCIDAD_VIENTO_10M']
        probabilidades = model.predict_proba(df_input[columnas_modelo])[:, 1]

        # 6. Formatear Respuesta Final
        detalle_tramos = []
        for idx, row in df_input.iterrows():
            prob = float(probabilidades[idx])
            riesgo = clasificar_riesgo(prob)

            detalle_tramos.append({
                "tramo": int(row['tramo']),
                "puntos_polyline": row['puntos_polyline'],
                "hora_paso": f"{row['hora_inicio']} - {row['hora_fin']}",
                "origen_coord": f"{row['lat_inicio']:.4f}, {row['lng_inicio']:.4f}",
                "destino_coord": f"{row['lat_fin']:.4f}, {row['lng_fin']:.4f}",
                "clima": {
                    "sensacion_termica": row['SENSACION_TERMICA'],
                    "lluvia": row['LLUVIA'],
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