import os
import math
import requests
import numpy as np
import pandas as pd
import googlemaps

# Carga de centroides
CENTROIDES_PATH = os.path.join("modelo", "centroides_zonas.csv")
if os.path.exists(CENTROIDES_PATH):
    centroides_df = pd.read_csv(CENTROIDES_PATH)
    LATS_CENTROIDES = centroides_df['LATITUD_CENTROIDE'].values
    LNGS_CENTROIDES = centroides_df['LONGITUD_CENTROIDE'].values
    ZONAS_IDS = centroides_df['ZONA_CIUDAD'].values

def obtener_zona_mas_cercana(lat_punto: float, lng_punto: float) -> int:
    distancias = (LATS_CENTROIDES - lat_punto)**2 + (LNGS_CENTROIDES - lng_punto)**2
    indice_minimo = np.argmin(distancias)
    return int(ZONAS_IDS[indice_minimo])

def obtener_clima_tramo(lat, lng, hora_paso):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat, "longitude": lng,
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

            dir_sin = math.sin(math.radians(dir_viento_grados))
            dir_cos = math.cos(math.radians(dir_viento_grados))

            return temp, precip, nubosidad, presion, v_viento, dir_sin, dir_cos

    except Exception:
        pass
    return 15.0, 0.0, 50.0, 750.0, 10.0, 0.0, 1.0

def obtener_direcciones_gmaps(origen, destino, departure_time):
    GOOGLE_APIKEY = os.getenv("GOOGLE_APIKEY")
    if not GOOGLE_APIKEY:
        raise ValueError("GOOGLE_APIKEY no configurada.")
    
    gmaps = googlemaps.Client(key=GOOGLE_APIKEY)
    directions = gmaps.directions(origen, destino, mode="driving", departure_time=departure_time)
    return directions