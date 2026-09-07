import os
import joblib
import polyline
import pandas as pd
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from zoneinfo import ZoneInfo

# Importaciones locales
from api.schemas import SolicitudRuta
from api.utils import segmentar_ruta
from api.services import obtener_zona_mas_cercana, obtener_clima_tramo, obtener_direcciones_gmaps

app = FastAPI(
    title="API PrediRuta - Riesgo Vial Bogotá",
    version="3.1.0",
    description="Backend modularizado con inferencia MLP (11 variables)."
)

# Constantes de negocio
DISTANCIA_TRAMO_KM = 3.2  # Se calcula como raiz(AreaUrbanaBogota/Clusters)*2=raiz(384/150)*2=3.2
UMBRAL_BAJO, UMBRAL_MEDIO = 0.3, 0.6

# Carga de modelo
MODEL_PATH = os.path.join("modelo", "modelo_ocurrencia_temporal.joblib")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el modelo en {MODEL_PATH}")
model = joblib.load(MODEL_PATH)

def clasificar_riesgo(prob: float):
    if prob < UMBRAL_BAJO:
        return {"nivel": "Bajo", "color": "green"}
    elif prob < UMBRAL_MEDIO:
        return {"nivel": "Medio", "color": "orange"}
    return {"nivel": "Alto", "color": "red"}

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API PrediRuta operativa"}

@app.post("/predict")
def procesar_y_predecir_ruta(data: SolicitudRuta):
    try:
        # 1. Parsing de fecha y hora con Zona Horaria
        tz_bogota = ZoneInfo("America/Bogota")
        fecha_dt = datetime.strptime(data.fecha_salida, "%Y-%m-%d").date()
        hora_dt = datetime.strptime(data.hora_salida, "%H:%M").time()
        
        # Combinar y forzar la zona horaria de Bogotá
        departure_time = datetime.combine(fecha_dt, hora_dt).replace(tzinfo=tz_bogota)

        # 2. Consulta a Google Maps
        directions = obtener_direcciones_gmaps(data.origen, data.destino, departure_time)
        if not directions:
            raise HTTPException(status_code=404, detail="No se encontró una ruta válida.")

        leg = directions[0]['legs'][0]
        points_decoded = polyline.decode(directions[0]['overview_polyline']['points'])

        # 3. Segmentación de ruta con la constante global
        tramos_segmentados = segmentar_ruta(points_decoded, DISTANCIA_TRAMO_KM)
        duracion_seg = leg['duration']['value']
        seg_por_tramo = duracion_seg / len(tramos_segmentados) if tramos_segmentados else 0

        # 4. Construcción de Dataset
        registros = []
        hora_acumulada = departure_time

        for idx, tramo_pts in enumerate(tramos_segmentados):
            h_inicio = hora_acumulada
            h_fin = hora_acumulada + timedelta(seconds=seg_por_tramo)
            hora_acumulada = h_fin

            lat_in, lng_in = tramo_pts[0]
            lat_out, lng_out = tramo_pts[-1]

            temp, precip, nubosidad, presion, v_viento, dir_sin, dir_cos = obtener_clima_tramo(lat_in, lng_in, h_inicio)
            zona = obtener_zona_mas_cercana(lat_in, lng_in)

            registros.append({
                "tramo": idx + 1,
                "puntos_polyline": tramo_pts,
                "hora_paso": f"{h_inicio.strftime('%H:%M')} - {h_fin.strftime('%H:%M')}",
                "origen_coord": f"{lat_in:.4f}, {lng_in:.4f}",
                "destino_coord": f"{lat_out:.4f}, {lng_out:.4f}",
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

        # 5. Inferencia
        columnas_modelo = [
            'ZONA_CIUDAD', 'MES', 'DIA_SEMANA', 'HORA', 
            'TEMPERATURA_2M', 'PRECIPITACION', 'NUBOSIDAD', 
            'PRESION_SUPERFICIE', 'VELOCIDAD_VIENTO_10M', 
            'DIRECCION_VIENTO_10M_SIN', 'DIRECCION_VIENTO_10M_COS'
        ]
        probabilidades = model.predict_proba(df_input[columnas_modelo])[:, 1]

        # 6. Formateo de Respuesta
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-mlp", tags=["Pruebas"])
def test_modelo_mlp():
    """
    Endpoint de prueba precargado con 3 tramos de ejemplo para verificar 
    que el modelo MLP de 11 variables realiza la inferencia correctamente.
    """

    datos_prueba = [
        {
            "tramo_id": "Tramo 1 - Mañana Despejada",
            "ZONA_CIUDAD": 1, "MES": 9, "DIA_SEMANA": 6, "HORA": 8,
            "TEMPERATURA_2M": 14.5, "PRECIPITACION": 0.0, "NUBOSIDAD": 20.0,
            "PRESION_SUPERFICIE": 750.0, "VELOCIDAD_VIENTO_10M": 5.0,
            "DIRECCION_VIENTO_10M_SIN": 0.0, "DIRECCION_VIENTO_10M_COS": 1.0
        },
        {
            "tramo_id": "Tramo 2 - Tarde Lluviosa",
            "ZONA_CIUDAD": 4, "MES": 9, "DIA_SEMANA": 6, "HORA": 15,
            "TEMPERATURA_2M": 18.2, "PRECIPITACION": 5.5, "NUBOSIDAD": 85.0,
            "PRESION_SUPERFICIE": 748.5, "VELOCIDAD_VIENTO_10M": 15.0,
            "DIRECCION_VIENTO_10M_SIN": 0.7071, "DIRECCION_VIENTO_10M_COS": -0.7071
        },
        {
            "tramo_id": "Tramo 3 - Noche Fría y Ventosa",
            "ZONA_CIUDAD": 8, "MES": 9, "DIA_SEMANA": 6, "HORA": 23,
            "TEMPERATURA_2M": 9.5, "PRECIPITACION": 0.0, "NUBOSIDAD": 10.0,
            "PRESION_SUPERFICIE": 752.0, "VELOCIDAD_VIENTO_10M": 25.0,
            "DIRECCION_VIENTO_10M_SIN": -1.0, "DIRECCION_VIENTO_10M_COS": 0.0
        }
    ]

    df_input = pd.DataFrame(datos_prueba)
    
    columnas_modelo = [
        'ZONA_CIUDAD', 'MES', 'DIA_SEMANA', 'HORA', 
        'TEMPERATURA_2M', 'PRECIPITACION', 'NUBOSIDAD', 
        'PRESION_SUPERFICIE', 'VELOCIDAD_VIENTO_10M', 
        'DIRECCION_VIENTO_10M_SIN', 'DIRECCION_VIENTO_10M_COS'
    ]

    try:
        probabilidades = model.predict_proba(df_input[columnas_modelo])[:, 1]
        
        resultados = []
        for idx, row in df_input.iterrows():
            prob = float(probabilidades[idx])
            riesgo = clasificar_riesgo(prob)
            
            resultados.append({
                "escenario": row["tramo_id"],
                "entradas": row[columnas_modelo].to_dict(),
                "prediccion": {
                    "probabilidad": round(prob, 4),
                    "nivel_riesgo": riesgo["nivel"],
                    "color": riesgo["color"]
                }
            })
            
        return {
            "status": "ok", 
            "mensaje": "Inferencia MLP exitosa", 
            "resultados": resultados
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la inferencia de prueba: {str(e)}")