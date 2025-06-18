# distancia.py  ·  streamlit run distancia.py
import os
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import distance
from folium.plugins import MarkerCluster

st.set_page_config(page_title="Hospital más cercano · València")

# ---------- 1. CARGAR DATOS (con caché) ----------
@st.cache_data(show_spinner=False)
def load_hospitals(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";")
    df = df[df["geo_point_2d"].notna() & df["geo_point_2d"].str.contains(",")]
    df[["LATITUD", "LONGITUD"]] = (
        df["geo_point_2d"].str.split(",", expand=True).astype(float)
    )
    return df[["Nombre", "LATITUD", "LONGITUD"]]

df = load_hospitals(os.path.join("./data/csv/hospitales.csv"))

# ---------- 2. CONSTRUIR EL MAPA ----------
m = folium.Map(
    location=[df["LATITUD"].mean(), df["LONGITUD"].mean()],
    zoom_start=13,
    tiles="OpenStreetMap",
    control_scale=True,
)
marker_cluster = MarkerCluster().add_to(m)

for row in df.itertuples():
    folium.Marker(
        [row.LATITUD, row.LONGITUD],
        popup=f"<strong>Nombre:</strong> {row.Nombre}",
        icon=folium.Icon(color="cadetblue", icon="info-sign"),
    ).add_to(marker_cluster)

# ---------- 3. ¿HAY UN CLIC PREVIO GUARDADO? ----------
if "click" in st.session_state:
    lat = st.session_state["click"]["lat"]
    lon = st.session_state["click"]["lng"]

    # 3a. Calcular hospital más cercano
    df["dist_m"] = df.apply(
        lambda r: distance((lat, lon), (r.LATITUD, r.LONGITUD)).meters, axis=1
    )
    nearest = df.loc[df.dist_m.idxmin()]

    # 3b. Pintar marcador del clic y del hospital
    folium.Marker(
        [lat, lon],
        icon=folium.Icon(color="blue", icon="glyphicon-screenshot"),
        popup="Aquí has pinchado",
    ).add_to(m)

    folium.Marker(
        [nearest.LATITUD, nearest.LONGITUD],
        icon=folium.Icon(color="green", icon="info-sign"),
        popup=f"{nearest.Nombre} ({nearest.dist_m:,.0f} m)",
    ).add_to(m)

    st.success(f"Hospital más cercano: {nearest.Nombre} – {nearest.dist_m:,.0f} m")

# ---------- 4. MOSTRAR MAPA Y CAPTAR NUEVO CLIC ----------
st.markdown("### 🌍 Mapa interactivo")
result = st_folium(m, height=600, width=1100, key="main_map")

# Si el usuario acaba de pinchar, guardar coordenadas y forzar rerun
if result and result["last_clicked"]:
    st.session_state["click"] = result["last_clicked"]
    st.rerun()
