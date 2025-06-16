import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# --- Configuración de la app y estilo general ---
st.set_page_config(page_title="Mapa Interactivo", layout="wide")

st.markdown("""
<style>
body {
    background-color: #f5f5f5;
}
</style>
""", unsafe_allow_html=True)

# --- Diccionarios de configuración ---
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

# --- Interfaz de navegación ---
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

    st.markdown("### 🌍 Vista del mapa")
    folium_static(mapa, width=1100, height=600)

    with st.expander("📊 Ver tabla de datos"):
        columnas_mostrar = [col for col in info_util["popup"] if col in df.columns]
        columnas_mostrar += ['LATITUD', 'LONGITUD']
        st.dataframe(df[columnas_mostrar])

elif seccion == "📊 Vulnerabilidad por barrios":
    st.markdown("## 🔍 Análisis de Vulnerabilidad por Barrios")

    vuln_df = pd.read_csv("./data/csv/vulnerabilidad-por-barrios.csv", sep=";")
    vuln_df = vuln_df[vuln_df['geo_point_2d'].notna() & vuln_df['geo_point_2d'].str.contains(',')]
    vuln_df[['LATITUD', 'LONGITUD']] = vuln_df['geo_point_2d'].str.split(',', expand=True).astype(float)

    mapa = folium.Map(location=[vuln_df['LATITUD'].astype(float).mean(), vuln_df['LONGITUD'].astype(float).mean()],
                      zoom_start=12, tiles="OpenStreetMap")

    for _, row in vuln_df.iterrows():
        color = {
            "Vulnerabilidad Alta": "red",
            "Vulnerabilidad Media": "orange",
            "Vulnerabilidad Baja": "green"
        }.get(row["Vul_Global"], "gray")

        folium.CircleMarker(
            location=[float(row["LATITUD"]), float(row["LONGITUD"])],
            radius=8,
            popup=f"<strong>{row['Name']}</strong><br>Distrito: {row['District']}<br>Índice global: {row['Ind_Global']}<br>{row['Vul_Global']}",
            tooltip=row["Name"],
            color=color,
            fill=True,
            fill_opacity=0.7
        ).add_to(mapa)

    st.markdown("### 🌐 Mapa de vulnerabilidad global por barrio")
    folium_static(mapa, width=1100, height=600)

    st.markdown("### 📈 Distribución de niveles de vulnerabilidad")
    fig, ax = plt.subplots()
    vuln_df['Vul_Global'].value_counts().plot(kind='bar', color=["green", "orange", "red"], ax=ax)
    plt.title("Número de barrios por nivel de vulnerabilidad global")
    plt.xlabel("Nivel de vulnerabilidad")
    plt.ylabel("Número de barrios")
    st.pyplot(fig)

    st.markdown("### 🧾 Tabla de indicadores por barrio")
    columnas = ["Name", "District", "Ind_Global", "Vul_Global", "Ind_Econom", "Vul_Econom", "Ind_Equip", "Vul_Equip"]
    st.dataframe(vuln_df[columnas])
