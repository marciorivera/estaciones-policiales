import sqlite3
from math import radians, sin, cos, sqrt, atan2

import streamlit as st
from streamlit_geolocation import streamlit_geolocation

DB_PATH = "estaciones.db"


# ---------- Servicio: cargar datos desde la base de datos ----------
@st.cache_data
def cargar_estaciones():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT nombre, ciudad, lat, lon, telefono FROM estaciones")
    filas = [dict(row) for row in cur.fetchall()]
    conn.close()
    return filas


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

# ---------- Valores por defecto en sesión ----------
if "lat" not in st.session_state:
    st.session_state.lat = 15.5042
if "lon" not in st.session_state:
    st.session_state.lon = -88.0250

st.subheader("📍 Usar mi ubicación (GPS)")
st.caption("Tu navegador te pedirá permiso de ubicación.")
gps = streamlit_geolocation()

if gps and gps.get("latitude") is not None and gps.get("longitude") is not None:
    st.session_state.lat = gps["latitude"]
    st.session_state.lon = gps["longitude"]
    st.success(f"Ubicación detectada: {gps['latitude']:.6f}, {gps['longitude']:.6f}")

st.divider()
st.subheader("O ingresa las coordenadas manualmente")

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitud", value=st.session_state.lat, format="%.6f", key="lat_input")
with col2:
    lon = st.number_input("Longitud", value=st.session_state.lon, format="%.6f", key="lon_input")

limite = st.slider("Cantidad de resultados a mostrar", min_value=1, max_value=len(estaciones), value=3)

if st.button("Buscar", type="primary"):
    cercanas = estaciones_mas_cercanas(lat, lon, estaciones, limite)

    st.subheader("Resultados")
    for i, est in enumerate(cercanas, start=1):
        tel = f" · 📞 {est['telefono']}" if est.get("telefono") else ""
        st.markdown(f"**{i}. {est['nombre']}** ({est['ciudad']}) — {est['distancia_km']} km{tel}")

    st.map(
        [{"lat": e["lat"], "lon": e["lon"]} for e in cercanas] + [{"lat": lat, "lon": lon}]
    )

with st.expander("Ver todas las estaciones registradas"):
    st.json(estaciones)
