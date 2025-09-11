# TerraSynapse - Frontend Enterprise (Streamlit)
# SPA com abas, hero premium, OpenWeather OneCall + AQI, alertas inteligentes
# Compatível com: /login, /register, /dashboard/{lat}/{lon}, /market

import streamlit as st
import requests
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ============================== Config ==============================
st.set_page_config(
    page_title="TerraSynapse - Plataforma Agrícola Enterprise",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------- BRAND / THEME ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
:root{
  --ts-green:#22c55e;
  --ts-green-600:#16a34a;
  --ts-bg:#0F172A;
  --ts-card:#0B1320;
  --ts-text:#E5E7EB;
  --ts-muted:#94A3B8;
}
html, body, [class*="css"] { font-family: 'Inter', system-ui; color: var(--ts-text); }
section.main > div { padding-top:.3rem; }

/* NAV TOP */
.ts-nav {
  position: sticky; top: 0; z-index: 100;
  background: linear-gradient(180deg, rgba(15,23,42,.98), rgba(15,23,42,.88));
  border-bottom: 1px solid rgba(148,163,184,.12);
  backdrop-filter: blur(6px);
  margin: -10px -16px 10px -16px; padding: 8px 18px;
}
.ts-nav .inner { display:flex; align-items:center; gap:.9rem; }
.ts-pill { border:1px solid rgba(148,163,184,.25); border-radius:999px; padding:.35rem .7rem; color:#94A3B8; font-size:.82rem;}
.ts-links { margin-left:auto; display:flex; flex-wrap:wrap; gap:.35rem; }
.ts-link { text-decoration:none; color:#94A3B8; padding:.4rem .7rem; border-radius:10px; border:1px solid transparent; }
.ts-link:hover{ border-color:rgba(148,163,184,.25); color:#E5E7EB; }

/* HERO */
.ts-hero{
  position:relative; overflow:hidden;
  background: linear-gradient(180deg, rgba(11,19,32,.9), rgba(11,19,32,.55));
  border-radius: 18px; padding: 22px 26px;
  border: 1px solid rgba(148,163,184,.15);
}

/* KPI */
.ts-kpi{
  background: linear-gradient(180deg, rgba(17,24,39,.6), rgba(17,24,39,.35));
  border: 1px solid rgba(148,163,184,.12);
  backdrop-filter: blur(6px);
  border-radius: 14px; padding: 12px 14px;
}

/* badge */
.ts-badge{ display:inline-flex;align-items:center;gap:.45rem; padding:.35rem .7rem;border-radius:999px;border:1px solid rgba(148,163,184,.25); color:#94A3B8; font-size:.78rem;}
.ts-dot{width:.55rem;height:.55rem;border-radius:50%;}
.ts-dot.green{background:#22c55e}

/* FOOTER */
.footer{ margin-top: 30px; padding: 18px; border-top:1px solid rgba(148,163,184,.18); color:#94A3B8;}
</style>
""", unsafe_allow_html=True)

# ============================== ENV/URLs ==============================
ENV_MODE = st.secrets.get("env", {}).get("MODE", "prod")
API_CFG   = st.secrets.get("api", {})
BACKEND_URL = (
    API_CFG.get("API_BASE_URL_PROD")
    if ENV_MODE == "prod"
    else API_CFG.get("API_BASE_URL_DEV", API_CFG.get("API_BASE_URL_PROD", API_CFG.get("API_BASE_URL", "")))
).rstrip("/") if API_CFG else ""
if not BACKEND_URL:
    st.error("API_BASE_URL não configurado em st.secrets.")
    st.stop()

def api_url(path: str) -> str:
    return f"{BACKEND_URL}{path}"

# ============================== HTTP Helpers ==============================
def _request(method, endpoint, json=None, token=None, timeout=20):
    url = api_url(endpoint)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=timeout)
        else:
            r = requests.post(url, headers=headers, json=json, timeout=timeout)
        try: body = r.json()
        except Exception: body = r.text
        return r.status_code, body
    except requests.exceptions.RequestException as e:
        return 0, {"detail": f"connection_error: {e}"}

# ============================== Geo ==============================
def geo_por_ip():
    try:
        r = requests.get("https://ipapi.co/json/", timeout=8)
        if r.status_code == 200:
            d = r.json()
            return float(d["latitude"]), float(d["longitude"]), d.get("city",""), d.get("region","")
    except Exception:
        pass
    g = st.secrets.get("geo", {})
    return float(g.get("DEFAULT_LAT", -15.78)), float(g.get("DEFAULT_LON", -47.93)), \
           g.get("DEFAULT_CITY","Brasília"), g.get("DEFAULT_STATE","DF")

def geocode_openweather(cidade:str, uf:str):
    key = st.secrets.get("openweather", {}).get("API_KEY", "")
    if not key:
        return None
    try:
        url = "https://api.openweathermap.org/geo/1.0/direct"
        params = {"q": f"{cidade},{uf},BR", "limit": 1, "appid": key}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200 and isinstance(r.json(), list) and r.json():
            d = r.json()[0]
            return float(d["lat"]), float(d["lon"])
    except Exception:
        pass
    return None

# ============================== OpenWeather OneCall + AQI ==============================
@st.cache_data(ttl=300)
def ow_fetch(lat: float, lon: float):
    """Retorna pacote com current/hourly/daily/alerts + AQI e chuva 24h."""
    key = st.secrets.get("openweather", {}).get("API_KEY", "")
    if not key:
        return {}
    base = "https://api.openweathermap.org/data/2.5"
    # OneCall
    one = {}
    try:
        params = {"lat":lat, "lon":lon, "appid":key, "units":"metric", "lang":"pt_br", "exclude":"minutely"}
        r = requests.get(f"{base}/onecall", params=params, timeout=12)
        if r.ok: one = r.json()
    except Exception:
        pass
    # AQI
    aqi = {}
    try:
        r2 = requests.get(f"{base}/air_pollution", params={"lat":lat, "lon":lon, "appid":key}, timeout=8)
        if r2.ok: aqi = r2.json()
    except Exception:
        pass
    # chuva 24h (hora a hora)
    precip_24h = 0.0
    try:
        for h in (one.get("hourly") or [])[:24]:
            precip_24h += float(h.get("rain", {}).get("1h", 0)) + float(h.get("snow", {}).get("1h", 0))
    except Exception:
        pass
    # AQI label
    aqi_label = None
    try:
        idx = int(aqi["list"][0]["main"]["aqi"])
        aqi_label = {1:"Bom",2:"Aceitável",3:"Moderado",4:"Ruim",5:"Muito Ruim"}.get(idx)
    except Exception:
        pass
    return {"one":one, "aqi":aqi, "aqi_label":aqi_label, "precip24":round(precip_24h,1)}

# ============================== Sessão ==============================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_token" not in st.session_state: st.session_state.user_token = None
if "user_data"  not in st.session_state: st.session_state.user_data  = None
if "loc" not in st.session_state:
    lat, lon, cidade, uf = geo_por_ip()
    st.session_state.loc = {"mode":"ip", "lat":lat, "lon":lon, "cidade":cidade, "uf":uf}
if "auto_refresh" not in st.session_state: st.session_state.auto_refresh = False

# ============================== Status (badge) ==============================
health_code, _ = _request("GET", "/health")
online_badge = '<span class="ts-badge"><span class="ts-dot" style="background:#22c55e"></span> ONLINE</span>' if health_code == 200 \
               else '<span class="ts-badge" style="color:#f87171;border-color:#f87171">OFFLINE</span>'

# ============================== NAV TOP + HERO ==============================
wm_dark  = "assets/brand/terrasynapse-wordmark-dark.svg"
hero     = "assets/brand/terrasynapse-hero-dark.svg"

st.markdown(f"""
<div class="ts-nav">
  <div class="inner">
    <img src="{wm_dark}" alt="TerraSynapse" style="height:24px;filter:drop-shadow(0 0 6px rgba(255,255,255,.12));" />
    <span class="ts-pill">{ENV_MODE.upper()} • {BACKEND_URL}</span>
    {online_badge}
    <div class="ts-links">
      <a class="ts-link" href="#dashboard">Dashboard</a>
      <a class="ts-link" href="#clima">Clima</a>
      <a class="ts-link" href="#vegetacao">Vegetação</a>
      <a class="ts-link" href="#mercado">Mercado</a>
      <a class="ts-link" href="#rent">Rentabilidade</a>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="ts-hero">
  <img src="{hero}" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:.9;" />
  <div style="position:relative; display:flex; align-items:center; gap:16px; z-index:1;">
    <img src="{wm_dark}" alt="TerraSynapse" style="height:54px; filter: drop-shadow(0 0 12px rgba(255,255,255,.15));" />
    <div style="margin-left:auto; display:flex; gap:.6rem; align-items:center;">
      <span class="ts-pill">{ENV_MODE.upper()} • {BACKEND_URL}</span>
      {online_badge}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
st.write("")

# ============================== Sidebar (Portal + Localização) ==============================
with st.sidebar:
    st.header("🔐 Portal Executivo")

    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["🔑 Login", "👤 Cadastro"])

        with tab1:
            email = st.text_input("📧 Email Corporativo", key="login_email")
            password = st.text_input("🔒 Senha", type="password", key="login_password")
            if st.button("🚀 Entrar", type="primary", use_container_width=True):
                if email and password:
                    code, body = _request("POST", "/login", json={"email": email, "password": password})
                    if code == 200 and isinstance(body, dict) and "access_token" in body:
                        st.session_state.logged_in = True
                        st.session_state.user_token = body["access_token"]
                        st.session_state.user_data = body["user"]
                        st.success("✅ Login realizado com sucesso!")
                        time.sleep(0.3); st.rerun()
                    else:
                        st.error("❌ Credenciais inválidas ou API indisponível.")
                else:
                    st.warning("⚠️ Preencha todos os campos")

        with tab2:
            nome = st.text_input("👤 Nome Completo")
            email_reg = st.text_input("📧 Email")
            password_reg = st.text_input("🔒 Senha", type="password")
            perfil = st.selectbox("🎯 Perfil Profissional",
                                  ["Produtor Rural","Agrônomo","Técnico Agrícola","Consultor",
                                   "Cooperativa","Gerente Agrícola","Outro"])
            empresa = st.text_input("🏢 Empresa")
            cidade  = st.text_input("🌍 Cidade", value=st.secrets.get("geo",{}).get("DEFAULT_CITY",""))
            estado  = st.selectbox("📍 Estado",
                                   ["SP","MG","MT","GO","MS","PR","RS","SC","BA","TO","MA","PI","CE","RN",
                                    "PB","PE","AL","SE","ES","RJ","AC","RO","AM","RR","PA","AP","DF"],
                                   index=1 if st.secrets.get("geo",{}).get("DEFAULT_STATE","MG")=="MG" else 0)
            if st.button("🎯 Criar Conta Enterprise", type="primary", use_container_width=True):
                if nome and email_reg and password_reg:
                    payload = {
                        "nome_completo": nome, "email": email_reg, "password": password_reg,
                        "perfil_profissional": perfil, "empresa_propriedade": empresa,
                        "cidade": cidade, "estado": estado
                    }
                    code, body = _request("POST", "/register", json=payload)
                    if code == 200 and isinstance(body, dict) and "access_token" in body:
                        st.session_state.logged_in = True
                        st.session_state.user_token = body["access_token"]
                        st.session_state.user_data = body["user"]
                        st.success("✅ Conta criada com sucesso!")
                        time.sleep(0.3); st.rerun()
                    else:
                        st.error("❌ Erro no cadastro")
                else:
                    st.warning("⚠️ Preencha os obrigatórios")
    else:
        st.success(f"👋 Bem-vindo, {st.session_state.user_data['nome']}!")

        with st.expander("📍 Localização de Trabalho", expanded=True):
            mode = st.radio("Modo", ["Automática (IP)", "Cidade/UF (precisa)", "Coordenadas"], horizontal=True)
            if mode == "Automática (IP)":
                if st.button("Detectar por IP"):
                    lat, lon, cidade, uf = geo_por_ip()
                    st.session_state.loc.update({"mode":"ip","lat":lat,"lon":lon,"cidade":cidade,"uf":uf})
                    st.success(f"Local: {cidade}-{uf} • {lat:.4f}, {lon:.4f}"); st.rerun()
            elif mode == "Cidade/UF (precisa)":
                c1,c2 = st.columns(2)
                with c1: c = st.text_input("Cidade", value=st.session_state.loc.get("cidade","Capinópolis"))
                with c2: u = st.selectbox("UF",
                    ["MG","SP","GO","MT","MS","PR","RS","SC","BA","TO","MA","PI","CE","RN","PB","PE","AL","SE","ES","RJ","AC","RO","AM","RR","PA","AP","DF"],
                    index=0 if st.session_state.loc.get("uf","MG")=="MG" else 1)
                if st.button("📡 Buscar Coordenadas (OpenWeather)"):
                    coords = geocode_openweather(c, u)
                    if coords:
                        lat, lon = coords
                        st.session_state.loc.update({"mode":"geo","lat":lat,"lon":lon,"cidade":c,"uf":u})
                        st.success(f"Local: {c}-{u} • {lat:.4f}, {lon:.4f}"); st.rerun()
                    else:
                        st.error("Não foi possível geocodificar. Verifique a API KEY do OpenWeather em secrets.")
            else:
                c1,c2 = st.columns(2)
                with c1: lat = st.number_input("Latitude", value=float(st.session_state.loc["lat"]), format="%.6f")
                with c2: lon = st.number_input("Longitude", value=float(st.session_state.loc["lon"]), format="%.6f")
                if st.button("Usar estas coordenadas"):
                    st.session_state.loc.update({"mode":"manual","lat":lat,"lon":lon})
                    st.success(f"Local setado • {lat:.4f}, {lon:.4f}"); st.rerun()

        st.toggle("⚡ Auto-refresh a cada 45s", key="auto_refresh")
        if st.session_state.auto_refresh:
            st.experimental_singleton.clear()  # segurança
            st.experimental_rerun()

# ============================== Funções de dados ==============================
def fetch_dashboard_data():
    lat = st.session_state.loc["lat"]; lon = st.session_state.loc["lon"]
    # Backend (clima+ndvi+mercado+rentabilidade)
    code, dash = _request("GET", f"/dashboard/{lat}/{lon}", token=st.session_state.user_token)
    if not (code == 200 and isinstance(dash, dict) and dash.get("status") == "success"):
        return None
    data = dash["data"]
    # OpenWeather extra
    ow = ow_fetch(lat, lon)
    data["_ow"] = ow

    # Alertas inteligentes (agrega)
    alertas = list(data.get("alertas", []))

    # 1) alertas oficiais do OneCall
    for al in (ow.get("one", {}).get("alerts") or []):
        nome = al.get("event", "Alerta meteorológico")
        alertas.append({"tipo":"meteo","prioridade":"alta","mensagem":f"OpenWeather: {nome}"})

    # 2) heurísticas de risco (incêndios, calor, vento)
    cur = (ow.get("one", {}).get("current") or {})
    temp = float(cur.get("temp", data["clima"]["temperatura"]))
    umid = float(cur.get("humidity", data["clima"]["umidade"]))
    vento = float(cur.get("wind_speed", data["clima"]["vento"])) * 3.6  # m/s -> km/h
    chuva24 = ow.get("precip24", 0.0)

    # Calor
    if temp >= 36 or (temp >= 34 and umid <= 25):
        alertas.append({"tipo":"calor","prioridade":"alta","mensagem":"Onda de calor — risco para planta e rebanho. Ajustar irrigação/sombreamento."})
    # Queimadas (ar seco + vento + sem chuva)
    if umid <= 25 and vento >= 20 and chuva24 < 1.0:
        alertas.append({"tipo":"queimadas","prioridade":"alta","mensagem":"Ar muito seco e ventos fortes, sem chuva nas últimas 24h — risco elevado de queimadas."})
    # Vento forte
    if vento >= 40:
        alertas.append({"tipo":"vento","prioridade":"media","mensagem":"Rajadas fortes — atenção a pulverizações e estruturas."})
    # Qualidade do ar
    if ow.get("aqi_label") in {"Ruim","Muito Ruim"}:
        alertas.append({"tipo":"qualidade_ar","prioridade":"media","mensagem":f"Qualidade do ar {ow['aqi_label']} — considerar manejo de poeira/fumaça."})

    data["alertas"] = alertas
    # extras para UI
    data["_extras"] = {"vento_kmh": round(vento,1), "chuva24": chuva24, "aqi_label": ow.get("aqi_label")}
    return data

# ============================== Páginas (abas) ==============================
def tab_dashboard(data):
    st.markdown('<div id="dashboard"></div>', unsafe_allow_html=True)
    lat = st.session_state.loc["lat"]; lon = st.session_state.loc["lon"]
    cid = st.session_state.loc.get("cidade",""); uf = st.session_state.loc.get("uf","")
    st.markdown(f'<span class="ts-badge"><span class="ts-dot green"></span> Local: {cid}-{uf} • {lat:.4f}, {lon:.4f}</span>', unsafe_allow_html=True)

    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("🔄 Atualizar Dados", type="primary"):
            st.cache_data.clear(); st.rerun()
    with c2:
        st.caption("Dica: altere a localização na barra lateral para atualizar o contexto.")

    st.markdown("---")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown('<div class="ts-kpi">', unsafe_allow_html=True)
        st.metric("🌡️ Temperatura", f"{data['clima']['temperatura']}°C", delta=f"Umidade: {data['clima']['umidade']}%")
        st.markdown('</div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="ts-kpi">', unsafe_allow_html=True)
        st.metric("💧 ET0", f"{data['clima']['et0']} mm/dia", delta=("Crítico" if data['clima']['et0'] > 6 else "Normal"))
        st.markdown('</div>', unsafe_allow_html=True)
    with k3:
        st.markdown('<div class="ts-kpi">', unsafe_allow_html=True)
        st.metric("🌱 NDVI", f"{data['vegetacao']['ndvi']}", delta=data['vegetacao']['status_vegetacao'])
        st.markdown('</div>', unsafe_allow_html=True)
    with k4:
        st.markdown('<div class="ts-kpi">', unsafe_allow_html=True)
        rec = data['rentabilidade']['receita_por_hectare']
        st.metric("💰 Receita/ha", f"R$ {rec:,.0f}", delta=f"{data['rentabilidade']['produtividade_estimada']} sc/ha")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("⚠️ Centro de Alertas Inteligentes")
    if data["alertas"]:
        for a in data["alertas"]:
            (st.error if a["prioridade"]=="alta" else st.warning)(a["mensagem"])
    else:
        st.success("✅ SISTEMA OPERACIONAL: Nenhum alerta crítico detectado.")

def tab_clima(data):
    st.markdown('<div id="clima"></div>', unsafe_allow_html=True)
    st.subheader("🌦️ Climatologia de Precisão")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown("##### Condições atuais")
        st.write(f"**Temperatura:** {data['clima']['temperatura']}°C")
        st.write(f"**Umidade:** {data['clima']['umidade']}%")
        st.write(f"**Vento:** {data['_extras']['vento_kmh']} km/h")
        st.write(f"**Pressão:** {data['clima']['pressao']} hPa")
        st.write(f"**Chuva 24h:** {data['_extras']['chuva24']} mm")
        if data["_extras"]["aqi_label"]:
            st.write(f"**Qualidade do ar:** {data['_extras']['aqi_label']}")
    with g2:
        st.markdown("##### ET0 (Evapotranspiração)")
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=data['clima']['et0'],
            title={'text': "ET0 (mm/dia)"}, delta={'reference': 5},
            gauge={'axis': {'range': [None, 10]},
                   'bar': {'color': "#22c55e"},
                   'steps': [{'range': [0,3], 'color': "#1f2937"},
                             {'range': [3,6], 'color': "#a3a3a3"},
                             {'range': [6,10], 'color': "#ef4444"}],
                   'threshold': {'line': {'color': "#ef4444", 'width': 4}, 'thickness': .75, 'value': 6}}
        ))
        fig.update_layout(height=260, margin=dict(l=10,r=10,t=30,b=0))
        st.plotly_chart(fig, use_container_width=True)
    with g3:
        st.markdown("##### Recomendação")
        st.info(f"**Irrigação:** {data['clima']['recomendacao_irrigacao']}")

def tab_ndvi(data):
    st.markdown('<div id="vegetacao"></div>', unsafe_allow_html=True)
    st.subheader("🛰️ NDVI Executivo")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### Status da Vegetação")
        st.write(f"**Valor:** {data['vegetacao']['ndvi']}")
        st.write(f"**Status:** {data['vegetacao']['status_vegetacao']}")
        st.write(f"**Data:** {data['vegetacao']['data_analise']}")
    with c2:
        st.markdown("##### Recomendações Técnicas")
        st.info(data['vegetacao']['recomendacao'])

def tab_mercado(data):
    st.markdown('<div id="mercado"></div>', unsafe_allow_html=True)
    st.subheader("📈 Mercado em Tempo Real (R$/saca)")
    com = data["mercado"]
    df = pd.DataFrame([
        {"Commodity":"Soja","Preço":com["soja"]["preco"]},
        {"Commodity":"Milho","Preço":com["milho"]["preco"]},
        {"Commodity":"Café","Preço":com["cafe"]["preco"]}
    ])
    figb = px.bar(df, x="Commodity", y="Preço", title=None)
    figb.update_layout(height=360, margin=dict(l=20,r=20,t=10,b=10))
    st.plotly_chart(figb, use_container_width=True)
    st.caption("Fonte: Yahoo Finance + Exchangerate.host (conversão USD/BRL).")

def tab_rent(data):
    st.markdown('<div id="rent"></div>', unsafe_allow_html=True)
    st.subheader("🤖 IA de Rentabilidade")
    c1, c2, c3 = st.columns(3)
    with c1: area = st.number_input("🌾 Área (hectares)", min_value=1, value=10)
    with c2: cultura = st.selectbox("🌱 Cultura Principal", ["Soja","Milho","Café"])
    with c3: prod = st.number_input("📊 Produtividade (sacas/ha)", min_value=1, value=50)
    if cultura.lower() in data['mercado']:
        preco = data['mercado'][cultura.lower()]['preco']
        receita_total = area * prod * preco
        custo_total   = area * 3000
        lucro_total   = receita_total - custo_total
        margem = (lucro_total/receita_total*100) if receita_total else 0
        m1,m2,m3 = st.columns(3)
        with m1: st.metric("Receita Total", f"R$ {receita_total:,.0f}")
        with m2: st.metric("Custo Estimado", f"R$ {custo_total:,.0f}")
        with m3: st.metric("Lucro Projetado", f"R$ {lucro_total:,.0f}")
        st.caption(f"**Área:** {area} ha | **Produtividade:** {prod} sc/ha | **Preço:** R$ {preco}/saca | **Margem:** {margem:.1f}%")

# ============================== Render ==============================
if st.session_state.logged_in:
    data = fetch_dashboard_data()
    if not data:
        st.error("❌ Não foi possível carregar os dados. Tente atualizar e confirme o token.")
    else:
        t1, t2, t3, t4, t5 = st.tabs(["📊 Dashboard", "🌦️ Clima", "🛰️ Vegetação", "💰 Mercado", "🧮 Rentabilidade"])
        with t1: tab_dashboard(data)
        with t2: tab_clima(data)
        with t3: tab_ndvi(data)
        with t4: tab_mercado(data)
        with t5: tab_rent(data)
else:
    # home institucional (resumo)
    st.subheader("TerraSynapse V2.0 Enterprise")
    st.caption("Plataforma Líder em Inteligência Agrícola")
    c1,c2,c3,c4 = st.columns(4)
    for col, title, value in [
        (c1, "Cobertura Climática", "🔭 200k+ localidades"),
        (c2, "Atualização", "⚡ ~15s"),
        (c3, "SLA", "99.9%"),
        (c4, "Segurança", "JWT + CORS")
    ]:
        with col:
            st.markdown('<div class="ts-kpi">', unsafe_allow_html=True)
            st.metric(title, value)
            st.markdown('</div>', unsafe_allow_html=True)
    st.info("Faça login no **Portal Executivo** (barra lateral) para acessar sua operação em tempo real.")

# ============================== Rodapé ==============================
st.markdown("""
<div class="footer">
  <div style="display:flex; flex-wrap:wrap; gap:10px; align-items:center;">
    <div>© TerraSynapse V2.0 — Plataforma Enterprise</div>
    <div style="margin-left:auto;">
      <a class="ts-pill" href="mailto:contato@terrasynapse.com">📩 contato@terrasynapse.com</a>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
