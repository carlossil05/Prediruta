# crea un archivo de python llamado 'app_mapa.py' y guarda todo el texto de abajo dentro de él".

#Librerias requeridas
import streamlit as st
import googlemaps
import polyline
import folium
from streamlit_folium import folium_static
import random
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Se obtiene la variable 'API_Google' del env
api_key = os.getenv("API_Google")

# Titulos y descripción de la página
st.set_page_config(page_title="PrediRuta", layout="wide")
st.title("PrediRuta")
st.markdown(""" 
PrediRuta es un sistema predictivo que permite estimar el nivel de riesgo vial 
asociado a una ruta dentro de Bogotá
""")

# --- Memoria del mapa---
if "mapa_calculado" not in st.session_state:
    st.session_state.mapa_calculado = None
if "detalles_ruta" not in st.session_state:
    st.session_state.detalles_ruta = ""

# Barra lateral para ingreso de información del usuario
st.sidebar.header("Parámetros de la Ruta")
origen = st.sidebar.text_input("Punto de Inicio", "Universidad Nacional de Colombia, Bogotá")
destino = st.sidebar.text_input("Destino", "Parque de la 93, Bogotá")
hora_salida = st.sidebar.time_input("Hora de salida", datetime.now().time())

# Función para simular el índice de riesgo mientras se define modelo
def obtener_color_riesgo():

    # Indice de riesgo aleatorio entre 0 y 1
    riesgo = random.random()

    if riesgo < 0.33:
        return "green", riesgo  # Riesgo Bajo
    elif riesgo < 0.66:
        return "orange", riesgo # Riesgo Medio
    else:
        return "red", riesgo    # Riesgo Alto


# --- BOTÓN DE CÁLCULO ---
if st.sidebar.button("Calcular Ruta y Riesgo"):

    #Si no hay API key
    if not api_key:
        st.sidebar.error("⚠️ La API Key es obligatoria para calcular la ruta.")
    else:

        #Spinner mientras calcula la ruta
        with st.spinner('Calculando ruta...'):

            try:

                #usa la libreria de googlemaps y la clave  de la API
                gmaps = googlemaps.Client(key=api_key)

                #
                departure_time = datetime.combine(datetime.now().date(), hora_salida)

                directions_result = gmaps.directions(
                    origen, destino, mode="driving", departure_time=departure_time
                )

                if directions_result:
                    route = directions_result[0]
                    legs = route['legs'][0]

                    start_lat = legs['start_location']['lat']
                    start_lng = legs['start_location']['lng']

                    # Creamos el mapa
                    m = folium.Map(location=[start_lat, start_lng], zoom_start=13)

                    # Marcadores
                    folium.Marker([start_lat, start_lng], tooltip="Inicio", icon=folium.Icon(color="blue", icon="play")).add_to(m)
                    folium.Marker([legs['end_location']['lat'], legs['end_location']['lng']], tooltip="Destino", icon=folium.Icon(color="red", icon="stop")).add_to(m)

                    # Tramos (Riesgos)
                    for step in legs['steps']:
                        path = polyline.decode(step['polyline']['points'])
                        color, riesgo = obtener_color_riesgo()
                        folium.PolyLine(locations=path, color=color, weight=6, opacity=0.8, tooltip=f"Riesgo: {riesgo:.2f}").add_to(m)

                    # GUARDAMOS EL RESULTADO EN LA MEMORIA
                    st.session_state.mapa_calculado = m
                    st.session_state.detalles_ruta = f"**Distancia total:** {legs['distance']['text']} | **Duración estimada:** {legs['duration']['text']}"

                else:
                    st.warning("No se encontró una ruta válida.")

            except Exception as e:
                st.error(f"Error al conectar con Google Maps: {e}")

# --- Render del mapa ---

if st.session_state.mapa_calculado is not None:
    folium_static(st.session_state.mapa_calculado, width=900, height=500)
    st.success(st.session_state.detalles_ruta)
else:
    mapa_por_defecto = folium.Map(location=[4.6482, -74.1953], zoom_start=11)
    folium_static(mapa_por_defecto, width=900, height=500)
