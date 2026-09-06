import os
import requests
import pandas as pd
import folium
import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_folium import st_folium

# --- CONFIGURACIÓN DE URL Y PÁGINA ---
API_URL = os.getenv("API_URL", "https://prediruta-api-carlos.up.railway.app/predict")

st.set_page_config(page_title="PrediRuta", layout="wide")
st.title("PrediRuta")
st.markdown(""" 
PrediRuta es un sistema predictivo que permite estimar el nivel de riesgo vial 
asociado a una ruta dentro de Bogotá.
""")

# --- ZONA HORARIA DE BOGOTÁ ---
tz_bogota = ZoneInfo("America/Bogota")
# Capturamos la hora actual sin segundos para validaciones exactas
ahora_bogota = datetime.now(tz_bogota).replace(second=0, microsecond=0)

# --- ESTADO DE SESIÓN ---
if "mapa_calculado" not in st.session_state:
    st.session_state.mapa_calculado = None
if "detalles_ruta" not in st.session_state:
    st.session_state.detalles_ruta = ""
if "tramos_info" not in st.session_state:
    st.session_state.tramos_info = []

# --- PARÁMETROS DE ENTRADA ---
st.sidebar.header("Parámetros de la Ruta")
origen = st.sidebar.text_input("Punto de Inicio", "Universidad Nacional de Colombia, Bogotá")
destino = st.sidebar.text_input("Destino", "Parque de la 93, Bogotá")

# Inputs de Fecha y Hora
fecha_salida = st.sidebar.date_input(
    "Fecha de salida", 
    value=ahora_bogota.date(), 
    min_value=ahora_bogota.date()
)
hora_salida = st.sidebar.time_input(
    "Hora de salida", 
    value=ahora_bogota.time()
)

# --- VALIDACIÓN DE TIEMPO EN EL FUTURO ---
# Combinamos la fecha y hora elegidas y le asignamos la zona horaria de Bogotá
dt_salida = datetime.combine(fecha_salida, hora_salida).replace(tzinfo=tz_bogota)
es_futuro = dt_salida >= ahora_bogota

if not es_futuro:
    st.sidebar.error("⚠️ La fecha y hora de salida deben ser en el futuro.")

# --- BOTÓN DE CÁLCULO ---
# Deshabilitamos visualmente la acción si el tiempo es inválido
if st.sidebar.button("Calcular Ruta y Riesgo", disabled=not es_futuro):
    with st.spinner('Consultando API y procesando riesgo...'):
        try:
            payload = {
                "origen": origen,
                "destino": destino,
                "fecha_salida": fecha_salida.strftime("%Y-%m-%d"),
                "hora_salida": hora_salida.strftime("%H:%M")
            }

            response = requests.post(API_URL, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                resumen = data["resumen"]
                tramos = data["tramos"]

                # Crear Mapa en Folium con la respuesta del backend
                start_loc = resumen["start_location"]
                end_loc = resumen["end_location"]

                m = folium.Map(location=[start_loc["lat"], start_loc["lng"]], zoom_start=13)
                folium.Marker([start_loc["lat"], start_loc["lng"]], tooltip="Inicio", icon=folium.Icon(color="blue", icon="play")).add_to(m)
                folium.Marker([end_loc["lat"], end_loc["lng"]], tooltip="Destino", icon=folium.Icon(color="red", icon="stop")).add_to(m)

                tramos_tabla = []

                for t in tramos:
                    # Dibujar tramo en el mapa
                    folium.PolyLine(
                        locations=t["puntos_polyline"],
                        color=t["color"],
                        weight=6,
                        opacity=0.8,
                        tooltip=f"Tramo {t['tramo']} - Hora: {t['hora_paso']} | Riesgo {t['nivel_riesgo']}: {t['probabilidad']:.2%}"
                    ).add_to(m)

                    # Estructurar fila para la tabla
                    tramos_tabla.append({
                        "Tramo": f"Tramo {t['tramo']}",
                        "Hora Paso": t["hora_paso"],
                        "Origen (Lat, Lng)": t["origen_coord"],
                        "Destino (Lat, Lng)": t["destino_coord"],
                        "Temperatura (°C)": f"{t['clima']['temperatura']:.1f}",
                        "Lluvia (mm)": f"{t['clima']['lluvia']:.1f}",
                        "Viento (km/h)": f"{t['clima']['viento']:.1f}",
                        "Riesgo": f"{t['probabilidad']:.2%}",
                        "Nivel": t["nivel_riesgo"]
                    })

                # Guardar en memoria de Streamlit
                st.session_state.mapa_calculado = m
                st.session_state.detalles_ruta = f"**Distancia total:** {resumen['distancia_total']} | **Duración estimada:** {resumen['duracion_estimada']} | **Tramos:** {resumen['total_tramos']} | **Riesgo Máximo:** {resumen['riesgo_maximo_ruta']:.2%}"
                st.session_state.tramos_info = tramos_tabla

            else:
                error_detail = response.json().get("detail", "Error desconocido en el servidor.")
                st.error(f"Error de la API ({response.status_code}): {error_detail}")

        except Exception as e:
            st.error(f"Error de conexión con el backend: {e}")

# --- RENDERING DE LA INTERFAZ ---
if st.session_state.mapa_calculado is not None:
    st_folium(st.session_state.mapa_calculado, width=900, height=500, returned_objects=[])
    st.success(st.session_state.detalles_ruta)

    st.subheader("📋 Detalle de Tramos de la Ruta")
    df_tramos = pd.DataFrame(st.session_state.tramos_info)
    st.dataframe(df_tramos, use_container_width=True)

else:
    mapa_por_defecto = folium.Map(location=[4.6482, -74.1953], zoom_start=11)
    st_folium(mapa_por_defecto, width=900, height=500, returned_objects=[])