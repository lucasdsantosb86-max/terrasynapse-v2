import os, datetime as dt
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="TerraSynapse V2.0", page_icon="🌱", layout="wide")

API = os.getenv("TS_API_URL", "").rstrip("/")

def safe_get(path, fallback):
    if not API:
        return fallback
    try:
        r = requests.get(f"{API}{path}", timeout=6)
        r.raise_for_status()
        return r.json()
    except Exception:
        return fallback

# ---------------------- mock/fallback ----------------------
weekly = pd.DataFrame([
    {"day":"Seg","temp":22,"humidity":65,"et0":3.8},
    {"day":"Ter","temp":25,"humidity":58,"et0":4.2},
    {"day":"Qua","temp":24,"humidity":62,"et0":4.0},
    {"day":"Qui","temp":26,"humidity":55,"et0":4.5},
    {"day":"Sex","temp":24,"humidity":68,"et0":4.2},
    {"day":"Sáb","temp":23,"humidity":72,"et0":3.9},
    {"day":"Dom","temp":25,"humidity":60,"et0":4.3},
])

commodity = pd.DataFrame([
    {"name":"Soja","price":165.50,"change":2.3},
    {"name":"Milho","price":75.80,"change":-1.2},
    {"name":"Café","price":1089.30,"change":4.1},
])

weather = safe_get("/weather/current", {
    "temperature": 24.5, "humidity": 68, "windSpeed": 12.3, "pressure": 1013.2,
    "et0": 4.2, "rainfall": 0, "condition": "Parcialmente nublado"
})
ndvi    = safe_get("/remote/ndvi", {"current":0.75,"trend":"+0.02","status":"Saudável"})
# -----------------------------------------------------------

# Sidebar (acesso executivo mock)
with st.sidebar:
    st.header("Portal Executivo")
    t1 = st.toggle("Login")
    st.text_input("Email Corporativo")
    st.text_input("Senha", type="password")
    st.button("Entrar")
    with st.expander("Diagnóstico do Sistema"):
        st.caption(f"TS_API_URL: {API or 'não definido'}")
        st.caption(f"Hora local: {dt.datetime.now():%d/%m/%Y %H:%M}")
        st.caption(f"Versão Streamlit: {st.__version__}")

# Título / hero
st.markdown("## 🌿 TerraSynapse V2.0")
st.caption("Plataforma Enterprise de Monitoramento Agrícola")
st.divider()

st.markdown("### 🌾 TerraSynapse V2.0 Enterprise")
st.caption("Plataforma Líder em Inteligência Agrícola")
st.write(
    "• **Monitoramento Climático** em tempo real com cálculo de evapotranspiração (ET₀) e recomendações de irrigação.  \n"
    "• **Análise por Satélite** (NDVI) para saúde da lavoura e alertas de estresse.  \n"
    "• **Inteligência de Mercado** com preços de commodities e tendências.  \n"
    "• **Dashboard Executivo** com visão 360° da propriedade."
)

# KPIs
c1, c2, c3 = st.columns(3)
c1.metric("🌡️ Temperatura", f"{weather['temperature']:.1f}°C",
          ("Ideal para cultivo" if 18 <= weather['temperature'] <= 28 else "Atenção"))
c2.metric("🌱 NDVI", f"{ndvi['current']:.2f}", ndvi.get("trend", ""))
c3.metric("🫘 Soja", f"R$ {commodity.loc[0,'price']:.2f}/sc",
          f"{commodity.loc[0,'change']:+.1f}%")

st.divider()

# Gráfico de tendências (temp x ET0)
gcol1, gcol2 = st.columns([2,1])
with gcol1:
    st.subheader("Tendências Climáticas (7 dias)")
    fig = px.line(
        weekly, x="day", y=["temp","et0"],
        labels={"value":"Valor","variable":"Série","day":"Dia"},
        markers=True
    )
    fig.update_traces(line_width=3)
    st.plotly_chart(fig, use_container_width=True)

with gcol2:
    st.subheader("Commodities (hoje)")
    for _, row in commodity.iterrows():
        st.metric(row["name"], f"R$ {row['price']:.2f}",
                  f"{row['change']:+.1f}%")

st.info("Dica: use o menu **Pages** (barra lateral) para acessar módulos como *Clima*, *Mercado* e *Sobre*.")
