# crea un archivo de python llamado 'app_mapa.py' y guarda todo el texto de abajo dentro de él".

# Librerias
import streamlit as st
import streamlit.components.v1 as components

#Titulo y layout de la página de streamlit en el navegador
st.set_page_config(page_title="Mi Mapa", layout="wide")

# Titulo.
st.title("Prueba streamlit Google Maps")

# html del mapa de google
mapa_html = """
<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d127255.43285098926!2d-74.19532884144369!3d4.648283717282869!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8e3f9bfd2da6cb29%3A0x239d635520a33914!2zQm9nb3TDoQ!5e0!3m2!1ses-419!2sco!4v1700000000000!5m2!1ses-419!2sco" width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
"""

# se usa el compoenente html de streamlit y el mapa
components.html(mapa_html, height=470)
