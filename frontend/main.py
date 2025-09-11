# TerraSynapse - Frontend Enterprise (Streamlit)
# Visual Enterprise + hero, navegação única por rotas (?view=), login/CTA,
# alerts agronômicos e páginas: dashboard, clima, vegetação, mercado, rentabilidade.
# Mantém compatibilidade com: /login, /register, /dashboard/{lat}/{lon}, /market

import streamlit as st
import requests
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="TerraSynapse - Plataforma Agrícola Enterprise",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# Theme / CSS
# ----------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
:root{
  --ts-green:#22c55e;
  --ts-green-600:#16a34a;
  --ts-ink:#0b1420;
  --ts-bg:#0F172A;
  --ts-card:#0B1320;
  --ts-outline:#1f2937;
  --ts-text:#E5E7EB;
  --ts-muted:#94A3B8;
  --ts-danger:#ef4444;
}
html, body, [class*="css"] { font-family: 'Inter', system-ui; color: var(--ts-text); }

/* Topbar */
.ts-topbar{
  position: sticky; top: 0; z-index: 1000;
  background: linear-gradient(180deg, rgba(15,23,42,.98), rgba(15,23,42,.88));
  border-bottom: 1px solid rgba(148,163,184,.12);
  backdrop-filter: blur(6px);
  margin: -10px -16px 12px -16px; padding: 10px 18px;
}
.ts-topbar .line{ display:flex; align-items:center; gap:12px; }
.ts-brand{ display:flex; align-items:center; gap:10px; font-weight:800; letter-spacing:-.02em; }
.ts-pill{
  border:1px solid rgba(148,163,184,.25); border-radius:999px; padding:.35rem .7rem;
  color:var(--ts-muted); font-size:.82rem;
}
.ts-links{ margin-left:auto; display:flex; gap:4px; flex-wrap:wrap; }
.ts-link{
  text-decoration:none; color:var(--ts-muted); padding:.45rem .75rem;
  border-radius:10px; border:1px solid transparent;
}
.ts-link.active{ color:var(--ts-text); border-color:rgba(148,163,184,.28); background:rgba(148,163,184,.06); }
.ts-link:hover{ border-color:rgba(148,163,184,.25); color:var(--ts-text); }

/* Hero */
.ts-hero{
  background:
    radial-gradient(1200px 520px at -10% -10%, rgba(34,211,238,.10), transparent 60%),
    radial-gradient(1100px 560px at 120% -20%, rgba(34,197,94,.12), transparent 60%),
    linear-gradient(180deg, rgba(11,19,32,.92), rgba(11,19,32,.55));
  padding: 20px 24px;
  border-radius: 18px;
  border: 1px solid rgba(148,163,184,.15);
  margin-bottom: 12px;
}

/* KPI */
.ts-kpi{
  background: linear-gradient(180deg, rgba(17,24,39,.6), rgba(17,24,39,.35));
  border: 1px solid rgba(148,163,184,.12);
  backdrop-filter: blur(6px);
  border-radius: 16px; padding: 16px 18px;
}

/* Cards */
.grid{ display:grid; gap:14px; grid-template-columns: repeat(12, 1fr); }
.card{
  grid-column: span 3 / span 3;
  background: linear-gradient(180deg, rgba(10,17,28,.6), rgba(10,17,28,.32));
  border: 1px solid rgba(148,163,184,.12);
  border-radius:16px; padding:18px 16px;
  transition: transform .15s ease, border .15s ease;
}
.card:hover{ transform: translateY(-2px); border-color: rgba(34,197,94,.35); }
.card h4{ margin:0 0 6px 0; font-weight:800; letter-spacing:-.01em;}
.card p { margin:.3rem 0 0 0; color:var(--ts-muted); font-size:.94rem;}

/* Badge */
.ts-badge{display:inline-flex;align-items:center;gap:.45rem;padding:.35rem .7rem;border-radius:999px;border:1px solid rgba(148,163,184,.25);color: var(--ts-muted);font-size:.78rem;}
.ts-dot{width:.55rem;height:.55rem;border-radius:50%;}
.ts-dot.green{background:var(--ts-green)}
.ts-dot.red{background:#ef4444}

/* CTA buttons */
.btn{
  display:inline-flex; align-items:center; gap:.55rem;
  padding:.70rem 1rem; border-radius:12px; font-weight:800;
  border:1px solid rgba(148,163,184,.22); text-decoration:none; transition: all .15s ease;
}
.btn.primary{ background:var(--ts-green); color:#04110a; border-color:transparent; }
.btn.primary:hover{ background:var(--ts-green-600);}
.btn.ghost{ background:transparent; color:var(--ts-text); }
.btn.ghost:hover{ border-color:rgba(148,163,184,.35); }

hr{border-color:rgba(148,163,184,.16);}
.footer{
  margin-top: 30px; padding: 18px;
  border-top:1px solid rgba(148,163,184,.18);
  color: var(--ts-muted);
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# ENV / API base
# ----------------------------------------------------------------------
ENV_MODE = st.secrets.get("env", {}).get("MODE", "prod")  # "prod" | "dev"
API_CFG   = st.secrets.get("api", {})
BACKEND_URL = (API_CFG.get("API_BASE_URL_PROD") if ENV_MODE == "prod"
               else API_CFG.get("API_BASE_URL_DEV")).rstrip("/") if API_CFG else st.secrets["api"]["API_BASE_URL"].rstrip("/")

def api_url(path: str) -> str:
    return f"{BACKEND_URL}{path}"

# ----------------------------------------------------------------------
# Helpers (HTTP, geo e assets)
# ----------------------------------------------------------------------
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
        try:
            body = r.json()
        except Exception:
            body = r.text
        return r.status_code, body
    except requests.exceptions.RequestException as e:
        return 0, {"detail": f"connection_error: {e}"}

def geo_por_ip():
    try:
        r = requests.get("https://ipapi.co/json/", timeout=8)
        if r.status_code == 200:
            d = r.json()
            return float(d["latitude"]), float(d["longitude"]), d.get("city",""), d.get("region","")
    except Exception:
        pass
    g = st.secrets.get("geo", {})
    return float(g.get("DEFAULT_LAT", -15.78)), float(g.get("DEFAULT_LON", -47.93)), g.get("DEFAULT_CITY","Brasília"), g.get("DEFAULT_STATE","DF")

def geocode_openweather(cidade:str, uf:str):
    key = st.secrets.get("openweather", {}).get("API_KEY", "")
    if not key: return None
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

ASSETS = Path("assets/brand")
def read_svg(name: str) -> str | None:
    p = ASSETS / name
    if p.exists():
        try:
            s = p.read_text(encoding="utf-8").strip()
            # garantia: declaração XML no topo sem espaços em branco antes
            if s.startswith("<svg") or s.startswith("<?xml") or "<svg" in s:
                return s if s.startswith("<svg") else s[s.find("<svg"):]
        except Exception:
            return None
    return None

def image_or_svg(svg_name: str, png_name: str, max_width: int = 1100):
    svg_html = read_svg(svg_name)
    if svg_html:
        st.markdown(f'<div style="max-width:{max_width}px">{svg_html}</div>', unsafe_allow_html=True)
    else:
        png = ASSETS / png_name
        if png.exists():
            st.image(str(png), use_container_width=False)

# ----------------------------------------------------------------------
# Sessão
# ----------------------------------------------------------------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_token" not in st.session_state: st.session_state.user_token = None
if "user_data"  not in st.session_state: st.session_state.user_data  = None
if "loc" not in st.session_state:
    lat, lon, cidade, uf = geo_por_ip()
    st.session_state.loc = {"mode":"ip", "lat":lat, "lon":lon, "cidade":cidade, "uf":uf}
if "auto_refresh" not in st.session_state: st.session_state.auto_refresh = False

# ----------------------------------------------------------------------
# Topbar (único – sem duplicação)
# ----------------------------------------------------------------------
health_code, _health = _request("GET", "/health")
online_badge = ('<span class="ts-badge"><span class="ts-dot green"></span> ONLINE</span>'
                if health_code == 200 else
                '<span class="ts-badge" style="color:#f87171;border-color:#f87171"><span class="ts-dot red"></span> OFFLINE</span>')

def link(view, label, current):
    cls = "ts-link active" if current==view else "ts-link"
    return f'<a class="{cls}" href="?view={view}">{label}</a>'

current_view = st.query_params.get("view", "dashboard")
st.markdown(f"""
<div class="ts-topbar">
  <div class="line">
    <div class="ts-brand">
      <!-- wordmark -->
      <div style="display:flex;align-items:center;gap:.5rem;">
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABC..." style="display:none" />
        <span>🌾</span><span>TerraSynapse</span>
      </div>
    </div>
    <span class="ts-pill">{ENV_MODE.upper()} • {BACKEND_URL}</span>
    {online_badge}
    <div class="ts-links">
      {link("dashboard","Dashboard", current_view)}
      {link("clima","Clima", current_view)}
      {link("vegetacao","Vegetação", current_view)}
      {link("mercado","Mercado", current_view)}
      {link("rent","Rentabilidade", current_view)}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Sidebar (Portal Executivo)
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("🔐 Portal Executivo")
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["🔑 Login", "👤 Cadastro"])

        with tab1:
            st.info("Bem-vindo ao **TerraSynapse** — Plataforma Enterprise de Inteligência Agrícola.\n\n"
                    "Acesse com seu email corporativo para ver clima, vegetação (NDVI), mercado e rentabilidade em tempo real.")
            email = st.text_input("📧 Email Corporativo", key="login_email")
            password = st.text_input("🔒 Senha", type="password", key="login_password")
            col_l, col_r = st.columns([1,1])
            if col_l.button("🚀 Entrar", type="primary", use_container_width=True):
                if email and password:
                    code, body = _request("POST", "/login", json={"email": email, "password": password})
                    if code == 200 and isinstance(body, dict) and "access_token" in body:
                        st.session_state.logged_in = True
                        st.session_state.user_token = body["access_token"]
                        st.session_state.user_data = body["user"]
                        st.success("✅ Login realizado com sucesso!")
                        st.query_params["view"] = "dashboard"
                        st.rerun()
                    else:
                        st.error("❌ Credenciais inválidas ou API indisponível.")
                else:
                    st.warning("⚠️ Preencha email e senha.")
            with col_r:
                st.markdown(
                    '<a class="btn ghost" href="https://wa.me/5534999729740" target="_blank">💬 Falar no WhatsApp</a>',
                    unsafe_allow_html=True
                )
            st.caption("Dúvidas: terrasynapse@terrasynapse.com • +55 34 9 9972-9740")

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
                                   index=1)
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
                        st.query_params["view"] = "dashboard"
                        st.rerun()
                    else:
                        st.error("❌ Erro no cadastro")
                else:
                    st.warning("⚠️ Preencha os obrigatórios")
    else:
        st.success(f"👋 Bem-vindo, {st.session_state.user_data['nome']}!")

        with st.expander("📍 Local de Trabalho", expanded=True):
            mode = st.radio("Modo", ["Automática (IP)", "Cidade/UF (precisa)", "Coordenadas"], horizontal=False)
            if mode == "Automática (IP)":
                if st.button("Detectar por IP"):
                    lat, lon, cidade, uf = geo_por_ip()
                    st.session_state.loc.update({"mode":"ip","lat":lat,"lon":lon,"cidade":cidade,"uf":uf})
                    st.success(f"Local: {cidade}-{uf} • {lat:.4f}, {lon:.4f}")
            elif mode == "Cidade/UF (precisa)":
                c1,c2 = st.columns(2)
                with c1: c = st.text_input("Cidade", value=st.session_state.loc.get("cidade","Capinópolis"))
                with c2: u = st.selectbox("UF", ["MG","SP","GO","MT","MS","PR","RS","SC","BA","TO","MA","PI","CE",
                                                 "RN","PB","PE","AL","SE","ES","RJ","AC","RO","AM","RR","PA","AP","DF"],
                                          index=0)
                if st.button("📡 Buscar Coordenadas (OpenWeather)"):
                    coords = geocode_openweather(c, u)
                    if coords:
                        lat, lon = coords
                        st.session_state.loc.update({"mode":"geo","lat":lat,"lon":lon,"cidade":c,"uf":u})
                        st.success(f"Local: {c}-{u} • {lat:.4f}, {lon:.4f}")
                    else:
                        st.error("Não foi possível geocodificar. Verifique a API KEY do OpenWeather em secrets.")
            else:
                c1,c2 = st.columns(2)
                with c1: lat = st.number_input("Latitude", value=float(st.session_state.loc["lat"]), format="%.6f")
                with c2: lon = st.number_input("Longitude", value=float(st.session_state.loc["lon"]), format="%.6f")
                if st.button("Usar estas coordenadas"):
                    st.session_state.loc.update({"mode":"manual","lat":lat,"lon":lon})
                    st.success(f"Local setado • {lat:.4f}, {lon:.4f}")

        st.checkbox("⚡ Auto-refresh a cada 45s", value=st.session_state.auto_refresh, key="auto_refresh")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.update({"logged_in": False, "user_token": None, "user_data": None})
            st.query_params["view"] = "dashboard"
            st.rerun()

# ----------------------------------------------------------------------
# Alerts agronômicos (regras simples + ET0)
# ----------------------------------------------------------------------
def agr_alerts(w: dict) -> list[dict]:
    alerts = []
    t = w.get("temperatura", 0) or 0
    u = w.get("umidade", 0) or 0
    v = w.get("vento", 0) or 0
    et0 = w.get("et0", 0) or 0

    # Calor severo + ar seco -> incêndio/estresse
    if t >= 36 and u <= 25 and v >= 12:
        alerts.append({"prioridade": "alta", "msg": "Risco de fogo/estresse térmico (calor ≥36°C, umidade ≤25%, vento ≥12 km/h). Reforçar vigilância e evitar queima."})
    # Déficit hídrico (ET0)
    if et0 >= 6:
        alerts.append({"prioridade": "alta", "msg": f"Déficit hídrico elevado (ET0 {et0} mm/dia). Planeje irrigação nas próximas horas."})
    elif et0 >= 4.5:
        alerts.append({"prioridade": "media", "msg": f"ET0 moderada ({et0} mm/dia). Monitorar lâminas de irrigação."})
    # Vento forte
    if v >= 35:
        alerts.append({"prioridade": "media", "msg": "Vento forte (≥35 km/h). Evite pulverização e atenção a estruturas."})
    # Ar muito seco
    if u <= 20 and t >= 32:
        alerts.append({"prioridade": "media", "msg": "Ar muito seco — ajuste planos de irrigação e manejo de poeira/fumaça."})

    return alerts

# ----------------------------------------------------------------------
# Data fetch (cache curto)
# ----------------------------------------------------------------------
@st.cache_data(ttl=60, show_spinner=False)
def get_dashboard(lat, lon, token):
    code, dash = _request("GET", f"/dashboard/{lat}/{lon}", token=token)
    return code, dash

# ----------------------------------------------------------------------
# Seções (views)
# ----------------------------------------------------------------------
def view_dashboard(data):
    st.subheader("📊 Dashboard Executivo — Tempo Real")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown('<div class="ts-kpi">', unsafe_allow_html=True)
        st.metric("🌡️ Temperatura", f"{data['clima']['temperatura']}°C", delta=f"Umidade: {data['clima']['umidade']}%")
        st.markdown('</div>', unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="ts-kpi">', unsafe_allow_html=True)
        st.metric("💧 ET0", f"{data['clima']['et0']} mm/dia",
                  delta=("Crítico" if data['clima']['et0'] > 6 else "Normal"))
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
    st.markdown("#### ⚠️ Centro de Alertas Inteligentes")
    alerts = agr_alerts(data["clima"])
    if alerts:
        for a in alerts:
            (st.error if a["prioridade"]=="alta" else st.warning)(a["msg"])
    else:
        st.success("✅ SISTEMA OPERACIONAL: Nenhum alerta crítico detectado.")

def view_clima(data):
    w = data["clima"]
    st.subheader("🌦️ Climatologia de Precisão")
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        st.markdown("##### Condições atuais")
        st.write(f"**Temperatura:** {w['temperatura']}°C")
        st.write(f"**Umidade:** {w['umidade']}%")
        st.write(f"**Vento:** {w['vento']} km/h")
        st.write(f"**Pressão:** {w['pressao']} hPa")
        st.write(f"**Condição:** {w['descricao']}")
    with c2:
        st.markdown("##### ET0 (Evapotranspiração)")
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=w['et0'],
            delta={'reference': 5},
            gauge={'axis': {'range': [None, 10]},
                   'bar': {'color': "#22c55e"},
                   'steps': [{'range': [0,3], 'color': "#1f2937"},
                             {'range': [3,6], 'color': "#9ca3af"},
                             {'range': [6,10], 'color': "#ef4444"}],
                   'threshold': {'line': {'color': "#ef4444", 'width': 4}, 'thickness': .75, 'value': 6}}
        ))
        fig.update_layout(height=280, margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c3:
        st.markdown("##### Recomendação")
        st.info(f"Irrigação: **{w['recomendacao_irrigacao']}**")
        for a in agr_alerts(w):
            (st.error if a["prioridade"]=="alta" else st.warning)(a["msg"])

def view_vegetacao(data):
    v = data["vegetacao"]
    st.subheader("🛰️ NDVI Executivo")
    c1, c2 = st.columns([1,1])
    with c1:
        st.write(f"**Valor:** {v['ndvi']}")
        st.write(f"**Status:** {v['status_vegetacao']}")
        st.write(f"**Data:** {v['data_analise']}")
    with c2:
        st.markdown("##### Recomendações Técnicas")
        st.info(v['recomendacao'])

def view_mercado(data):
    st.subheader("💰 Mercado em Tempo Real (R$/saca)")
    com = data["mercado"]
    df = pd.DataFrame([
        {"Commodity":"Soja","Preço":com["soja"]["preco"]},
        {"Commodity":"Milho","Preço":com["milho"]["preco"]},
        {"Commodity":"Café","Preço":com["cafe"]["preco"]}
    ])
    figb = px.bar(df, x="Commodity", y="Preço", title=None)
    figb.update_layout(height=420, margin=dict(l=20,r=20,t=10,b=10))
    st.plotly_chart(figb, use_container_width=True)
    st.caption("Fonte: Yahoo Finance + Exchangerate.host (conversão USD/BRL).")

def view_rent(data):
    st.subheader("🧮 IA de Rentabilidade")
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
        r1,r2,r3 = st.columns(3)
        r1.metric("Receita Total", f"R$ {receita_total:,.0f}")
        r2.metric("Custo Estimado", f"R$ {custo_total:,.0f}")
        r3.metric("Lucro Projetado", f"R$ {lucro_total:,.0f}")
        st.caption(f"Área: {area} ha | Produtividade: {prod} sc/ha | Preço: R$ {preco}/saca | Margem: {margem:.1f}%")

# ----------------------------------------------------------------------
# HERO (mostra para todos; renderiza wordmark + hero se disponíveis)
# ----------------------------------------------------------------------
def hero():
    st.markdown('<div class="ts-hero">', unsafe_allow_html=True)
    # Word-mark grande
    image_or_svg("terrasynapse-wordmark-light.svg", "terrasynapse-wordmark-light.png", max_width=820)
    # Hero waves / composição
    image_or_svg("terrasynapse-hero-dark.svg", "terrasynapse-hero-dark.png", max_width=1100)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Conteúdo principal
# ----------------------------------------------------------------------
# HERO sempre em cima (sem duplicação de menus)
hero()

if st.session_state.logged_in:
    # botão atualizar e auto-refresh
    lat = st.session_state.loc["lat"]; lon = st.session_state.loc["lon"]
    cidade = st.session_state.loc.get("cidade",""); uf = st.session_state.loc.get("uf","")

    cA, cB = st.columns([1,1])
    with cA:
        st.markdown(
            f'<span class="ts-badge"><span class="ts-dot green"></span> Local: {cidade}-{uf} • {lat:.4f}, {lon:.4f}</span>',
            unsafe_allow_html=True
        )
    with cB:
        if st.button("🔄 Atualizar Dados", type="primary"):
            get_dashboard.clear()
            st.rerun()

    if st.session_state.auto_refresh:
        time.sleep(45)
        get_dashboard.clear()
        st.rerun()

    code, dash = get_dashboard(lat, lon, st.session_state.user_token)
    if code == 200 and isinstance(dash, dict) and dash.get("status") == "success":
        data = dash["data"]
        # roteia
        if current_view == "dashboard":
            view_dashboard(data)
        elif current_view == "clima":
            view_clima(data)
        elif current_view == "vegetacao":
            view_vegetacao(data)
        elif current_view == "mercado":
            view_mercado(data)
        elif current_view == "rent":
            view_rent(data)
        else:
            view_dashboard(data)

        st.markdown("---")
        st.caption(f"TerraSynapse V2.0 — Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    else:
        st.error("❌ Não foi possível carregar o dashboard agora. Verifique o login e tente novamente.")
else:
    # home/marketing (não logado)
    st.markdown("### TerraSynapse V2.0 Enterprise")
    st.caption("Plataforma Líder em Inteligência Agrícola")

    # KPIs de vitrine
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

    st.markdown("---")
    st.markdown("#### Por que o TerraSynapse?")
    st.markdown('<div class="grid">', unsafe_allow_html=True)
    cards = [
        ("🌦️ Climatologia de Precisão", "Dados meteorológicos com ET0 para decisões de irrigação assertivas."),
        ("🛰️ NDVI Executivo", "Estado da vegetação por sazonalidade — monitoramento ágil do talhão."),
        ("📈 Mercado em Tempo Real", "Soja, milho e café com preços em R$/saca (conversão automática)."),
        ("🤖 IA de Rentabilidade", "Estimativas por cultura e produtividade — visão financeira imediata."),
    ]
    for title, txt in cards:
        st.markdown(f'<div class="card"><h4>{title}</h4><p>{txt}</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Rodapé
# ----------------------------------------------------------------------
st.markdown("""
<div class="footer">
  <div style="display:flex; flex-wrap:wrap; gap:10px; align-items:center; width:100%;">
    <div>© TerraSynapse V2.0 — Plataforma Enterprise</div>
    <div style="margin-left:auto; display:flex; gap:8px; flex-wrap:wrap;">
      <a class="ts-pill" href="mailto:terrasynapse@terrasynapse.com">📩 terrasynapse@terrasynapse.com</a>
      <a class="ts-pill" href="https://wa.me/5534999729740" target="_blank">📱 WhatsApp: (34) 9 9972-9740</a>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
