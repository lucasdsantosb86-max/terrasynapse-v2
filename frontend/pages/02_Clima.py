import streamlit as st
import plotly.express as px
from services.weather import get_weather

st.set_page_config(page_title="Clima", page_icon="⛅", layout="wide")

lat = float(st.secrets["site"]["lat"])
lon = float(st.secrets["site"]["lon"])
tz  = st.secrets["site"].get("timezone", "auto")

st.title("⛅ Monitoramento Climático")
w = get_weather(lat, lon, tz)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Temperatura (°C)", f"{w['current']['temperature']:.1f}")
col2.metric("Umidade (%)", f"{w['current']['humidity']:.0f}")
col3.metric("Vento (km/h)", f"{w['current']['wind']:.1f}")
col4.metric("Pressão (hPa)", f"{w['current']['pressure']:.0f}")

st.subheader("Tendências (7 dias)")
d = w["daily"].copy()
d.rename(columns={
    "et0_fao_evapotranspiration": "ET0 (mm/dia)",
    "temperature_2m_max": "Tmáx (°C)",
    "temperature_2m_min": "Tmín (°C)",
    "precipitation_sum": "Chuva (mm)"
}, inplace=True)

fig = px.line(
    d, x="time",
    y=["Tmáx (°C)", "Tmín (°C)", "ET0 (mm/dia)", "Chuva (mm)"],
    markers=True
)
fig.update_layout(legend_title="Variável", height=420)
st.plotly_chart(fig, use_container_width=True)
