import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import os

# ---------------- CONFIGURACIÓN DE PÁGINA ----------------
st.set_page_config(page_title="Mapa Interactivo", layout="wide")

# ---------------- TÍTULOS Y DESCRIPCIONES ----------------
TITULOS_DESCRIPCIONES = {
    "barris-policials.csv": (
        "🚓 Mapa Interactivo de Barrios Policiales",
        "Visualiza los barrios y su ubicación en el contexto policial de la ciudad."
    ),
    "hospitales.csv": (
        "🏥 Mapa de Hospitales",
        "Ubicación de los hospitales registrados en el sistema de salud."
    ),
    "dona.csv": (
        "🚺 Mapa de Recursos para la Mujer",
        "Visualiza puntos de interés y servicios orientados a la mujer."
    ),
    "migrants.csv": (
        "🌍 Mapa de Migración",
        "Datos geográficos relacionados con población migrante."
    ),
    "discapacitat-fisica.csv": (
        "🦽 Mapa de Discapacidad Física",
        "Recursos o ubicaciones vinculadas a personas con discapacidad física."
    ),
    "discapacitat-sensorial.csv": (
        "🦻 Mapa de Discapacidad Sensorial",
        "Recursos para personas con discapacidades sensoriales."
    ),
    "discapacitat-intellectual.csv": (
        "🧠 Mapa de Discapacidad Intelectual",
        "Ubicaciones relacionadas con servicios o población con discapacidad intelectual."
    ),
    "malaltia-mental.csv": (
        "🧘 Mapa de Salud Mental",
        "Visualización de datos relacionados con salud mental."
    ),
    "majors.csv": (
        "👴 Mapa de Personas Mayores",
        "Servicios y ubicaciones orientados a la población mayor."
    )
}

# ---------------- SELECCIÓN DE ARCHIVO ----------------
data_folder = "./data/csv/"
csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]
archivo_csv = st.selectbox("📁 Selecciona el archivo de datos:", csv_files)

# Título y descripción dinámica
titulo, descripcion = TITULOS_DESCRIPCIONES.get(
    archivo_csv, ("📍 Mapa Interactivo", "Mapa de datos geográficos"))
st.markdown(f"## {titulo}")
st.markdown(descripcion)

# ---------------- CARGA DE DATOS ----------------
df = pd.read_csv(os.path.join(data_folder, archivo_csv), sep=";")

# Limpiar y separar latitud y longitud
df = df[df['geo_point_2d'].notna() & df['geo_point_2d'].str.contains(',')]
df[['LATITUD', 'LONGITUD']] = df['geo_point_2d'].str.split(',', expand=True).astype(float)

# ---------------- RESUMEN DE DATOS ----------------
col1, col2, col3 = st.columns(3)
col1.metric("📍 Total de puntos", len(df))
col2.metric("📌 Columnas disponibles", len(df.columns))
col3.metric("🗂️ Archivo", archivo_csv)

# ---------------- CREACIÓN DEL MAPA ----------------
mapa_base = "OpenStreetMap"

mapa = folium.Map(
    location=[df['LATITUD'].mean(), df['LONGITUD'].mean()],
    zoom_start=13,
    tiles=mapa_base
)

marker_cluster = MarkerCluster().add_to(mapa)

# Marcadores con información detallada
for row in df.itertuples():
    nombre_barrio = getattr(row, 'Nom_Barri', 'Desconocido')
    districte = getattr(row, 'Nom_Districte', getattr(row, 'DISTRICTE', 'Sin distrito'))
    codigo = getattr(row, 'Codi_Barri', getattr(row, 'CODI_BARRI', 'N/A'))

    popup_text = f"""
    <strong>Barrio:</strong> {nombre_barrio}<br>
    <strong>Distrito:</strong> {districte}<br>
    <strong>Código:</strong> {codigo}
    """

    folium.Marker(
        location=[row.LATITUD, row.LONGITUD],
        popup=folium.Popup(popup_text, max_width=300),
        tooltip=f"{nombre_barrio} ({districte})",
        icon=folium.Icon(color='cadetblue', icon='info-sign')
    ).add_to(marker_cluster)

# ---------------- MOSTRAR MAPA ----------------
st.markdown("### 🌍 Mapa generado")
folium_static(mapa, width=1100, height=600)

# ---------------- MOSTRAR TABLA ----------------
with st.expander("📊 Mostrar tabla de datos"):
    columnas_mostrar = ['Nom_Barri', 'Nom_Districte', 'Codi_Barri', 'LATITUD', 'LONGITUD']
    columnas_mostrar = [col for col in columnas_mostrar if col in df.columns]
    st.dataframe(df[columnas_mostrar])
