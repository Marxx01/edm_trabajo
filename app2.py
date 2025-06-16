import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import streamlit as st
import pandas as pd
import os

# Configuración de la app
st.set_page_config(page_title="Mapa Interactivo", layout="wide")

# Títulos y descripciones según archivo
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

# Info útil para cada archivo
info_util_por_archivo = {
    "barris-policials": {
        "popup": ["Nombre", "Código"],
        "tooltip": "Nombre"
    },
    "hospitales": {
        "popup": ["Nombre", "Tipo", "Camas", "Financiaci", "Direccion"],
        "tooltip": "Nombre"
    },
    "discapacitat-fisica": {
        "popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"],
        "tooltip": "equipamien"
    },
    "discapacitat-intellectual": {
        "popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"],
        "tooltip": "equipamien"
    },
    "discapacitat-sensorial": {
        "popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"],
        "tooltip": "equipamien"
    },
    "dona": {
        "popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"],
        "tooltip": "equipamien"
    },
    "majors": {
        "popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"],
        "tooltip": "equipamien"
    },
    "malaltia-mental": {
        "popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"],
        "tooltip": "equipamien"
    },
    "migrants": {
        "popup": ["equipamien", "identifica", "telefono", "codvia", "numportal"],
        "tooltip": "equipamien"
    }
}

# Cargar archivos CSV disponibles
data_folder = "./data/csv"
csv_files = [f for f in os.listdir(data_folder) if f.endswith(".csv")]

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

# Selector visible
titulo_seleccionado = st.selectbox("📁 Selecciona el tipo de mapa:", list(opciones_selector.keys()))

# Nombre real del archivo
archivo_csv = opciones_selector[titulo_seleccionado]

# Cargar datos
df = pd.read_csv(os.path.join(data_folder, archivo_csv), sep=";")

# Procesar coordenadas
df = df[df['geo_point_2d'].notna() & df['geo_point_2d'].str.contains(',')]
df[['LATITUD', 'LONGITUD']] = df['geo_point_2d'].str.split(',', expand=True).astype(float)

# Título y descripción dinámicos
titulo, descripcion = TITULOS_DESCRIPCIONES.get(archivo_csv, ("📍 Mapa Interactivo", "Mapa de datos geográficos"))
st.markdown(f"## {titulo}")
st.markdown(descripcion)

# Mostrar métricas
col1, col2, col3 = st.columns(3)
col1.metric("📍 Total de puntos", len(df))
col2.metric("📌 Columnas", len(df.columns))
col3.metric("🗂️ Archivo", archivo_csv)

# Crear mapa (OpenStreetMap fijo)
mapa = folium.Map(
    location=[df['LATITUD'].mean(), df['LONGITUD'].mean()],
    zoom_start=13,
    tiles="OpenStreetMap"
)

# Añadir marcadores
marker_cluster = MarkerCluster().add_to(mapa)
key = archivo_csv.replace(".csv", "")
info_util = info_util_por_archivo.get(key)

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

# Mostrar mapa
st.markdown("### 🌍 Vista del mapa")
folium_static(mapa, width=1100, height=600)

# Tabla expandible
with st.expander("📊 Ver tabla de datos"):
    columnas_mostrar = [col for col in info_util["popup"] if col in df.columns]
    columnas_mostrar += ['LATITUD', 'LONGITUD']
    st.dataframe(df[columnas_mostrar])
