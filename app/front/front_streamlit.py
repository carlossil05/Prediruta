# crea un archivo de python llamado 'app_mapa.py' y guarda todo el texto de abajo dentro de él".

#Librerias requeridas
import streamlit as st
import googlemaps
import polyline
import folium
from streamlit_folium import st_folium
import random
from datetime import datetime
import os
import math
import pandas as pd


# Se obtiene la variable 'API_Google' del env
api_key = os.getenv("GOOGLE_APIKEY")


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
if "tramos_info" not in st.session_state:
    st.session_state.tramos_info = []

# Barra lateral para ingreso de información del usuario
st.sidebar.header("Parámetros de la Ruta")
origen = st.sidebar.text_input("Punto de Inicio", "Universidad Nacional de Colombia, Bogotá")
destino = st.sidebar.text_input("Destino", "Parque de la 93, Bogotá")
hora_salida = st.sidebar.time_input("Hora de salida", datetime.now().time())

# Configuración de distancia de tramo
distancia_tramo_km = st.sidebar.number_input(
    "Distancia de cada tramo (km)", 
    min_value=0.1, 
    max_value=10.0, 
    value=1.0, 
    step=0.5,
    help="Modifica este valor para cambiar la longitud de segmentación de la ruta."
)

# --- Funciones Auxiliares Geográficas ---
def haversine_distance(coord1, coord2):
    """Calcula la distancia en kilómetros entre dos coordenadas (lat, lng)."""
    R = 6371.0  # Radio de la Tierra en km
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def interpolar_punto(p1, p2, fraccion):
    """Interpola un punto entre p1 y p2 según una fracción (0 a 1)."""
    lat = p1[0] + (p2[0] - p1[0]) * fraccion
    lng = p1[1] + (p2[1] - p1[1]) * fraccion
    return (lat, lng)

def segmentar_ruta(puntos_full, tamano_tramo_km):
    """
    Divide una lista de puntos (lat, lng) en tramos de longitud aproximada tamano_tramo_km.
    Retorna una lista de tramos, donde cada tramo es una lista de puntos.
    """
    if not puntos_full or len(puntos_full) < 2:
        return [puntos_full] if puntos_full else []

    tramos = []
    tramo_actual = [puntos_full[0]]
    dist_acumulada = 0.0

    for i in range(len(puntos_full) - 1):
        p_inicio = puntos_full[i]
        p_fin = puntos_full[i+1]
        dist_segmento = haversine_distance(p_inicio, p_fin)

        if dist_segmento == 0:
            continue

        p_cursor = p_inicio
        dist_restante = dist_segmento

        while dist_acumulada + dist_restante >= tamano_tramo_km:
            necesario = tamano_tramo_km - dist_acumulada
            fraccion = necesario / dist_restante
            p_corte = interpolar_punto(p_cursor, p_fin, fraccion)

            tramo_actual.append(p_corte)
            tramos.append(tramo_actual)

            # Iniciar nuevo tramo
            tramo_actual = [p_corte]
            dist_acumulada = 0.0
            p_cursor = p_corte
            dist_restante = haversine_distance(p_cursor, p_fin)

        if dist_restante > 0:
            tramo_actual.append(p_fin)
            dist_acumulada += dist_restante

    if len(tramo_actual) > 1:
        tramos.append(tramo_actual)

    return tramos


# Función para simular el índice de riesgo mientras se define modelo
def obtener_color_riesgo():
    # Índice de riesgo aleatorio entre 0 y 1
    riesgo = random.random()

    if riesgo < 0.3:
        return "green", riesgo, "Bajo"
    elif riesgo < 0.6:
        return "orange", riesgo, "Medio"
    else:
        return "red", riesgo, "Alto"


# --- BOTÓN DE CÁLCULO ---
if st.sidebar.button("Calcular Ruta y Riesgo"):

    #Si no hay API key
    if not api_key:
        st.sidebar.error("⚠️ Error de lectura de la API Key de Google maps")
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

                    # Polilínea completa de la ruta
                    polyline_str = route['overview_polyline']['points']
                    puntos_totales = polyline.decode(polyline_str)

                    # Segmentar ruta en tramos de N km
                    tramos_segmentados = segmentar_ruta(puntos_totales, distancia_tramo_km)

                    start_lat = legs['start_location']['lat']
                    start_lng = legs['start_location']['lng']

                    # Crear mapa Folium
                    m = folium.Map(location=[start_lat, start_lng], zoom_start=13)
                    folium.Marker([start_lat, start_lng], tooltip="Inicio", icon=folium.Icon(color="blue", icon="play")).add_to(m)
                    folium.Marker([legs['end_location']['lat'], legs['end_location']['lng']], tooltip="Destino", icon=folium.Icon(color="red", icon="stop")).add_to(m)

                    tramos_info = []

                    # Trazar cada tramo individualizado
                    for idx, tramo_pts in enumerate(tramos_segmentados, start=1):
                        color, riesgo, nivel = obtener_color_riesgo()
                        
                        # Dibujar en mapa
                        folium.PolyLine(
                            locations=tramo_pts, 
                            color=color, 
                            weight=6, 
                            opacity=0.8, 
                            tooltip=f"Tramo {idx} ({distancia_tramo_km} km) - Riesgo {nivel}: {riesgo:.2f}"
                        ).add_to(m)

                        # Guardar información del tramo para la tabla
                        lat_inicio, lng_inicio = tramo_pts[0]
                        lat_fin, lng_fin = tramo_pts[-1]
                        
                        tramos_info.append({
                            "Tramo": f"Tramo {idx}",
                            "Origen (Lat, Lng)": f"{lat_inicio:.4f}, {lng_inicio:.4f}",
                            "Destino (Lat, Lng)": f"{lat_fin:.4f}, {lng_fin:.4f}",
                            "Riesgo": f"{riesgo:.2%}",
                            "Nivel": nivel
                        })

                    # Guardar en estado
                    st.session_state.mapa_calculado = m
                    st.session_state.detalles_ruta = f"**Distancia total:** {legs['distance']['text']} | **Duración estimada:** {legs['duration']['text']} | **Tramos generados:** {len(tramos_segmentados)}"
                    st.session_state.tramos_info = tramos_info

                else:
                    st.warning("No se encontró una ruta válida.")

            except Exception as e:
                st.error(f"Error al conectar con Google Maps: {e}")

# --- MOSTRAR RESULTADOS ---

if st.session_state.mapa_calculado is not None:
    # Mostrar mapa
    st_folium(st.session_state.mapa_calculado, width=900, height=500, returned_objects=[])
    st.success(st.session_state.detalles_ruta)

    # Mostrar la lista/tabla de tramos generados
    st.subheader("📋 Detalle de Tramos de la Ruta")
    df_tramos = pd.DataFrame(st.session_state.tramos_info)
    st.dataframe(df_tramos, use_container_width=True)

else:
    mapa_por_defecto = folium.Map(location=[4.6482, -74.1953], zoom_start=11)
    st_folium(mapa_por_defecto, width=900, height=500, returned_objects=[])
