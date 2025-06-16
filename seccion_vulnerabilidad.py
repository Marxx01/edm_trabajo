import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import folium
from streamlit_folium import folium_static
from folium import GeoJson, GeoJsonTooltip

# =================== CSS Personalizado ===================
st.markdown("""
<style>
body {
    background-color: #eef2f5;
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3 {
    color: #2c3e50;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
.stDataFrame {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =================== Título de la sección ===================
st.title("📊 Vulnerabilidad por Barrios")
st.markdown("Análisis geográfico y estadístico de vulnerabilidad en los barrios de la ciudad.")

# =================== Selector de funcionalidad ===================
feature = st.sidebar.selectbox("Selecciona una funcionalidad", ["Mapa interactivo", "Gráficos", "Tabla de datos"])

# =================== Carga de datos con cache ===================
@st.cache_data
def cargar_datos():
    df = pd.read_csv("./data/csv/vulnerabilidad-por-barrios.csv", sep=";")
    df = df[df['geo_point_2d'].notna() & df['geo_point_2d'].str.contains(',')]
    df[['LATITUD', 'LONGITUD']] = df['geo_point_2d'].str.split(',', expand=True).astype(float)
    df["geometry"] = df["Geo Shape"].apply(json.loads)
    df["color"] = df["Vul_Global"].apply(get_color)
    return df

def get_color(vul):
    return {
        "Vulnerabilidad Alta": "red",
        "Vulnerabilidad Media": "orange",
        "Vulnerabilidad Baja": "green"
    }.get(vul, "gray")

vuln_df = cargar_datos()

# =================== Mapa ===================
if feature == "Mapa interactivo":
    st.subheader("🌍 Mapa por nivel de vulnerabilidad global")

    mapa = folium.Map(location=[vuln_df['LATITUD'].mean(), vuln_df['LONGITUD'].mean()],
                      zoom_start=12, tiles="OpenStreetMap")

    for _, row in vuln_df.iterrows():
        geojson = {
            "type": "Feature",
            "geometry": row["geometry"],
            "properties": {
                "Barrio": row["Name"],
                "Distrito": row["District"],
                "Índice Global": row["Ind_Global"],
                "Vulnerabilidad": row["Vul_Global"],
                "color": row["color"]
            }
        }
        GeoJson(
            geojson,
            style_function=lambda feature: {
                "fillColor": feature["properties"]["color"],
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.5
            },
            tooltip=GeoJsonTooltip(fields=["Barrio", "Distrito", "Índice Global", "Vulnerabilidad"])
        ).add_to(mapa)

    folium_static(mapa, width=1100, height=600)

# =================== Gráficos ===================
elif feature == "Gráficos":
    st.subheader("📊 Distribución por tipos de vulnerabilidad")
    categorical_cols = ["Vul_Equip", "Vul_Dem", "Vul_Econom", "Vul_Global"]
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 10))
    axes = axes.flatten()

    for i, col in enumerate(categorical_cols):
        ax = axes[i]
        counts = vuln_df[col].value_counts()
        counts.plot(kind='bar', ax=ax, color=["green", "orange", "red"])
        for idx, value in enumerate(counts.values):
            ax.text(idx, value + 0.5, str(value), ha='center', va='bottom', fontsize=9)
        ax.set_title(col.replace("Vul_", "Vulnerabilidad "))
        ax.set_ylabel("Nº de barrios")
        ax.set_xlabel("")
        ax.grid(axis='y')

    plt.tight_layout()
    st.pyplot(fig)

    st.subheader("📈 Indicadores numéricos de vulnerabilidad")
    numerical_cols = ["Ind_Equip", "Ind_Dem", "Ind_Econom", "Ind_Global"]
    fig2, axes2 = plt.subplots(nrows=2, ncols=2, figsize=(10, 5))
    axes2 = axes2.flatten()

    for i, col in enumerate(numerical_cols):
        axes2[i].boxplot(vuln_df[col].dropna(), patch_artist=True,
                         boxprops=dict(facecolor="#3498db", color="black"),
                         medianprops=dict(color="black"))
        axes2[i].set_title(col.replace("Ind_", "Índice "))
        axes2[i].grid(True)

    plt.tight_layout()
    st.pyplot(fig2)

# =================== Tabla de datos ===================
elif feature == "Tabla de datos":
    st.subheader("🧾 Tabla de indicadores por barrio")
    cols = ["Name", "District", "Ind_Equip", "Vul_Equip", "Ind_Dem", "Vul_Dem", "Ind_Econom", "Vul_Econom", "Ind_Global", "Vul_Global"]
    st.dataframe(vuln_df[cols])

    # Botón para descargar CSV
    st.download_button(
        "📥 Descargar datos como CSV",
        data=vuln_df[cols].to_csv(index=False),
        file_name="vulnerabilidad_barrios.csv",
        mime="text/csv"
    )
