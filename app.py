import json
from math import radians, sin, cos, sqrt, atan2

import streamlit as st

# ---------- Servicio: cargar datos ----------
@st.cache_data
def cargar_estaciones():
    with open("estaciones.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- Servicio: calcular distancia (Haversine) ----------
def distancia_km(lat1, lon1, lat2, lon2):
    R = 6371  # radio de la Tierra en km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


# ---------- Servicio: encontrar más cercanas ----------
def estaciones_mas_cercanas(lat, lon, estaciones, limite=3):
    resultado = []
    for est in estaciones:
        d = distancia_km(lat, lon, est["lat"], est["lon"])
        resultado.append({**est, "distancia_km": round(d, 2)})
    resultado.sort(key=lambda x: x["distancia_km"])
    return resultado[:limite]


# ---------- Interfaz (cliente) ----------
st.set_page_config(page_title="Estaciones Policiales Cercanas", page_icon="🚓")

st.title("🚓 Estaciones Policiales Más Cercanas")
st.write("Ingresa tu ubicación (latitud y longitud) para encontrar las 3 estaciones policiales más cercanas.")

estaciones = cargar_estaciones()

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitud", value=15.5042, format="%.6f")
with col2:
    lon = st.number_input("Longitud", value=-88.0250, format="%.6f")

limite = st.slider("Cantidad de resultados a mostrar", min_value=1, max_value=len(estaciones), value=3)

if st.button("Buscar", type="primary"):
    cercanas = estaciones_mas_cercanas(lat, lon, estaciones, limite)

    st.subheader("Resultados")
    for i, est in enumerate(cercanas, start=1):
        st.markdown(f"**{i}. {est['nombre']}** — {est['distancia_km']} km")

    st.map(
        [{"lat": e["lat"], "lon": e["lon"]} for e in cercanas] + [{"lat": lat, "lon": lon}]
    )

with st.expander("Ver todas las estaciones registradas"):
    st.json(estaciones)
