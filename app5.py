import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from folium import GeoJson, GeoJsonTooltip

import matplotlib.pyplot as plt
import json
import os

from streamlit_folium import st_folium
from geopy.distance import distance



# Configuración de la app
st.set_page_config(page_title="Mapa Interactivo", layout="wide")

# CSS global
st.markdown("""
<style>
body {
    background-color: #eef2f5;
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3 {
    color: #2c3e50;
}
</style>
""", unsafe_allow_html=True)

# Diccionarios
TITULOS_DESCRIPCIONES = {
    "barris-policials.csv": ("🚓 Mapa de Barrios Policiales", "Ubicación y códigos de los barrios."),
    "hospitales.csv": ("🏥 Mapa de Hospitales", "Hospitales por tipo, financiación y camas."),
    "dona.csv": ("🚺 Mapa de Recursos para la Mujer", "Ubicación de centros de apoyo para la mujer."),
    "migrants.csv": ("🌍 Mapa de Recursos para Migrantes", "Servicios de atención a población migrante."),
    "discapacitat-fisica.csv": ("🦽 Mapa de Discapacidad Física", "Centros relacionados con discapacidad física."),
    "discapacitat-sensorial.csv": ("🦻 Mapa de Discapacidad Sensorial", "Servicios para discapacidades sensoriales."),
    "discapacitat-intellectual.csv": ("🧠 Mapa de Discapacidad Intelectual", "Recursos para discapacidad intelectual."),
    "malaltia-mental.csv": ("🧘 Mapa de Salud Mental", "Centros de atención en salud mental."),
    "majors.csv": ("👴 Mapa de Servicios para Personas Mayores", "Recursos para la tercera edad.")
}

info_util_por_archivo = {
    "barris-policials": {"popup": ["Nombre", "Código"], "tooltip": "Nombre"},
    "hospitales": {"popup": ["Nombre", "Tipo", "Camas", "Financiaci", "Direccion"], "tooltip": "Nombre"},
    "discapacitat-fisica": {"popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"], "tooltip": "equipamien"},
    "discapacitat-intellectual": {"popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"], "tooltip": "equipamien"},
    "discapacitat-sensorial": {"popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"], "tooltip": "equipamien"},
    "dona": {"popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"], "tooltip": "equipamien"},
    "majors": {"popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"], "tooltip": "equipamien"},
    "malaltia-mental": {"popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"], "tooltip": "equipamien"},
    "migrants": {"popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"], "tooltip": "equipamien"}
}

opciones_selector = {
    "🚓 Mapa de Barrios Policiales": "barris-policials.csv",
    "🏥 Mapa de Hospitales": "hospitales.csv",
    "🚺 Mapa de Recursos para la Mujer": "dona.csv",
    "🌍 Mapa de Recursos para Migrantes": "migrants.csv",
    "🦽 Mapa de Discapacidad Física": "discapacitat-fisica.csv",
    "🦻 Mapa de Discapacidad Sensorial": "discapacitat-sensorial.csv",
    "🧠 Mapa de Discapacidad Intelectual": "discapacitat-intellectual.csv",
    "🧘 Mapa de Salud Mental": "malaltia-mental.csv",
    "👴 Mapa de Servicios para Personas Mayores": "majors.csv"
}

# Menú lateral
seccion = st.sidebar.radio("Selecciona una sección", ["🗺️ Mapas de servicios", "📊 Vulnerabilidad por barrios"])

if seccion == "🗺️ Mapas de servicios":
    titulo_vis = st.selectbox("Selecciona el tipo de mapa:", list(opciones_selector.keys()))
    archivo_csv = opciones_selector[titulo_vis]
    key = archivo_csv.replace(".csv", "")
    info_util = info_util_por_archivo.get(key)

    df = pd.read_csv(os.path.join("./data/csv", archivo_csv), sep=";")
    df = df[df['geo_point_2d'].notna() & df['geo_point_2d'].str.contains(',')]
    df[['LATITUD', 'LONGITUD']] = df['geo_point_2d'].str.split(',', expand=True).astype(float)

    titulo, descripcion = TITULOS_DESCRIPCIONES.get(archivo_csv, ("📍 Mapa Interactivo", "Mapa de datos geográficos"))
    st.markdown(f"## {titulo}")
    st.markdown(descripcion)

    col1, col2, col3 = st.columns(3)
    col1.metric("📍 Total de puntos", len(df))
    col2.metric("📌 Columnas", len(df.columns))
    col3.metric("🗂️ Archivo", archivo_csv)

    mapa = folium.Map(location=[df['LATITUD'].mean(), df['LONGITUD'].mean()], zoom_start=13, tiles="OpenStreetMap")
    marker_cluster = MarkerCluster().add_to(mapa)

    for row in df.itertuples():
        popup_parts = []
        for col in info_util["popup"]:
            valor = getattr(row, col, "N/D")
            popup_parts.append(f"<strong>{col}:</strong> {valor}")
        popup_html = "<br>".join(popup_parts)
        tooltip_val = getattr(row, info_util["tooltip"], "")
        folium.Marker(
            location=[row.LATITUD, row.LONGITUD],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=tooltip_val,
            icon=folium.Icon(color="cadetblue", icon="info-sign")
        ).add_to(marker_cluster)


    if "click" in st.session_state:
        lat = st.session_state["click"]["lat"]
        lon = st.session_state["click"]["lng"]

        # 3a. Calcular hospital más cercano
        df["dist_m"] = df.apply(
            lambda r: distance((lat, lon), (r.LATITUD, r.LONGITUD)).meters, axis=1
        )
        nearest = df.loc[df.dist_m.idxmin()]

        nombre= nearest.Nombre if 'Nombre' in df.columns else nearest.equipamien
        # 3b. Pintar marcador del clic y del hospital
        folium.Marker(
            [lat, lon],
            icon=folium.Icon(color="blue", icon="glyphicon-screenshot"),
            popup="Aquí has pinchado",
        ).add_to(mapa)

        folium.Marker(
            [nearest.LATITUD, nearest.LONGITUD],
            icon=folium.Icon(color="green", icon="info-sign"),
            popup=f"{nombre} ({nearest.dist_m:,.0f} m)",
        ).add_to(mapa)

        st.success(f"Centro más cercano: {nombre} – {nearest.dist_m:,.0f} m")


    st.markdown("### 🌍 Vista del mapa")

    result = st_folium(mapa, height=600, width=1100, key="main_map")
    if result and result["last_clicked"]:
        st.session_state["click"] = result["last_clicked"]
        st.rerun()
    with st.expander("📊 Ver tabla de datos"):
        columnas_mostrar = [col for col in info_util["popup"] if col in df.columns]
        columnas_mostrar += ['LATITUD', 'LONGITUD']
        st.dataframe(df[columnas_mostrar])

elif seccion == "📊 Vulnerabilidad por barrios":
    exec(open("./seccion_vulnerabilidad.py", encoding="utf-8").read())