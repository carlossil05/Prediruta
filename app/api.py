#Librerias
import os
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

# Se inicializa la API
app = FastAPI(
    title="API PrediRuta - Riesgo Vial Bogotá",
    version="1.0.0"
)


# Se Carga modelo y artefactos al iniciar la aplicación
MODEL_PATH = os.path.join("modelo", "modelo_xgboost_bogota.joblib")
CENTROIDES_PATH = os.path.join("modelo", "centroides_zonas.csv")

if not os.path.exists(MODEL_PATH) or not os.path.exists(CENTROIDES_PATH):
    raise FileNotFoundError(" Los arvhios 'modelo_xgboost_bogota.joblib' y 'centroides_zonas.csv' no están en el directorio.")

#Se extrae el modelo predictivo
model = joblib.load(MODEL_PATH)

# Se extraen los centroides
centroides_df = pd.read_csv(CENTROIDES_PATH)

# Función para asignar coordenadas a las zonas de la ciudad
def obtener_zona_mas_cercana(lat_punto: float, lng_punto: float) -> int:

    # Se guardan las latitudes y longitudes de los centroides
    lats = centroides_df['LATITUD_CENTROIDE'].values
    lngs = centroides_df['LONGITUD_CENTROIDE'].values
    
    # Calcular la distancia euclidiana a todos los centroides
    distancias = (lats - lat_punto)**2 + (lngs - lng_punto)**2
    
    # Se obtiene el centroide con la menor distancia
    indice_minimo = np.argmin(distancias)
    
    #Se retorna el ID del centroide más cercano
    return int(centroides_df.iloc[indice_minimo]['ZONA_CIUDAD'])

#Guarda los ids de los centroides
zonas_ids = centroides_df['ZONA_CIUDAD'].values


#  Esquemas de datos
class CoordenadaConClima(BaseModel):
    lat: float = Field(..., example=4.6580)
    lng: float = Field(..., example=-74.0930)
    MES: int = Field(..., ge=1, le=12, example=9)
    DIA_SEMANA: int = Field(..., ge=0, le=6, example=2)
    HORA: int = Field(..., ge=0, le=23, example=18)
    SENSACION_TERMICA: float = Field(..., example=15.0)
    LLUVIA: float = Field(..., example=0.0)
    VELOCIDAD_VIENTO_10M: float = Field(..., example=8.5)

class PrediccionRutaInput(BaseModel):
    puntos_ruta: List[CoordenadaConClima]

    # Configuración de ejemplo dinámico para Swagger UI / ReDoc
    model_config = {
        "json_schema_extra": {
            "example": {
                "puntos_ruta": [
                    {
                        "lat": 4.6362,
                        "lng": -74.0837,
                        "MES": 9,
                        "DIA_SEMANA": 2,
                        "HORA": 3,
                        "SENSACION_TERMICA": 16.5,
                        "LLUVIA": 0.0,
                        "VELOCIDAD_VIENTO_10M": 7.2
                    },
                    {
                        "lat": 4.6482,
                        "lng": -74.0880,
                        "MES": 9,
                        "DIA_SEMANA": 2,
                        "HORA": 3,
                        "SENSACION_TERMICA": 16.0,
                        "LLUVIA": 0.1,
                        "VELOCIDAD_VIENTO_10M": 8.0
                    },
                    {
                        "lat": 4.6610,
                        "lng": -74.0925,
                        "MES": 9,
                        "DIA_SEMANA": 2,
                        "HORA": 4,
                        "SENSACION_TERMICA": 15.2,
                        "LLUVIA": 0.5,
                        "VELOCIDAD_VIENTO_10M": 9.1
                    },
                    {
                        "lat": 4.6725,
                        "lng": -74.0801,
                        "MES": 9,
                        "DIA_SEMANA": 2,
                        "HORA": 5,
                        "SENSACION_TERMICA": 14.8,
                        "LLUVIA": 1.2,
                        "VELOCIDAD_VIENTO_10M": 10.5
                    },
                    {
                        "lat": 4.6780,
                        "lng": -74.0560,
                        "MES": 9,
                        "DIA_SEMANA": 2,
                        "HORA": 6,
                        "SENSACION_TERMICA": 14.0,
                        "LLUVIA": 2.0,
                        "VELOCIDAD_VIENTO_10M": 11.0
                    }
                ]
            }
        }
    }

# --- CONSTANTES DE NEGOCIO Y CONFIGURACIÓN ---
UMBRAL_RIESGO_BAJO = 0.35
UMBRAL_RIESGO_MEDIO = 0.65

CONFIG_RIESGO = {
    "BAJO": {"nivel": "Bajo","color": "green"},
    "MEDIO": {"nivel": "Medio","color": "orange"},
    "ALTO": {"nivel": "Alto","color": "red"}
}

# Función auxiliar para clasificar la probabilidad usando las constantes
def clasificar_riesgo(probabilidad: float) -> dict:
    if probabilidad < UMBRAL_RIESGO_BAJO:
        return CONFIG_RIESGO["BAJO"]
    elif probabilidad < UMBRAL_RIESGO_MEDIO:
        return CONFIG_RIESGO["MEDIO"]
    else:
        return CONFIG_RIESGO["ALTO"]

# ENDPOINTS

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API PrediRuta operativa"}

@app.post("/predict")
def predecir_riesgo_ruta(data: PrediccionRutaInput):
    try:
        resultados_tramos = []

        #Se recorren todos los puntos de la ruta
        for idx, punto in enumerate(data.puntos_ruta):
            #Se obtiene la zona más cercana del punto
            zona_asignada = obtener_zona_mas_cercana(punto.lat, punto.lng)

            # Se extraen los datos de las variables predictoras
            input_df = pd.DataFrame([{
                'ZONA_CIUDAD': zona_asignada,
                'MES': punto.MES,
                'DIA_SEMANA': punto.DIA_SEMANA,
                'HORA': punto.HORA,
                'SENSACION_TERMICA': punto.SENSACION_TERMICA,
                'LLUVIA': punto.LLUVIA,
                'VELOCIDAD_VIENTO_10M': punto.VELOCIDAD_VIENTO_10M
            }])

            # Se predice la probabilidad de que ocurra un accidente
            probabilidad = float(model.predict_proba(input_df)[:, 1][0])

            # Se clasifica el nivel de riesgo
            info_riesgo = clasificar_riesgo(probabilidad)

            #Se agrega el resultado
            resultados_tramos.append({
                "tramo": idx,
                "lat": punto.lat,
                "lng": punto.lng,
                "zona_ciudad": zona_asignada,
                "probabilidad": round(probabilidad, 4),
                "nivel_riesgo": info_riesgo["nivel"],
                "color": info_riesgo["color"]
            })

        # Se pbtoeme el riesgo máximo
        riesgo_maximo = max([t["probabilidad"] for t in resultados_tramos]) if resultados_tramos else 0.0

        return {
            "riesgo_maximo_ruta": riesgo_maximo,
            "total_tramos": len(resultados_tramos),
            "detalle_tramos": resultados_tramos
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la inferencia: {str(e)}")