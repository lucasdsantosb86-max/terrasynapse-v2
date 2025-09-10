# TerraSynapse - Frontend Enterprise (Streamlit)
# Visual Enterprise ++ : hero premium, navegação de páginas, cards glass, CTA, rodapé
# Mantém compatibilidade com /login, /register, /weather, /satellite, /market, /dashboard

import streamlit as st
import requests
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ----------------------------------------------------------------------
# Configuração base
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="TerraSynapse - Plataforma Agrícola Enterprise",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------- BRAND / THEME ----------------------------
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
section.main > div { padding-top:.4rem; }

/* NAV TOP (ancoras internas) */
.ts-nav {
  position: sticky; top: 0; z-index: 100;
  background: linear-gradient(180deg, rgba(15,23,42,.98), rgba(15,23,42,.88));
  border-bottom: 1px solid rgba(148,163,184,.12);
  backdrop-filter: blur(6px);
  margin: -10px -16px 10px -16px; padding: 8px 18px;
}
.ts-nav .inner { display:flex; align-items:center; gap:.9rem; }
.ts-brand { display:flex; align-items:center; gap:.6rem; font-weight:800; letter-spacing:-.02em;}
.ts-pill {
  border:1px solid rgba(148,163,184,.25); border-radius:999px; padding:.35rem .7rem;
  color:var(--ts-muted); font-size:.82rem;
}
.ts-links { margin-left:auto; display:flex; flex-wrap:wrap; gap:.35rem; }
.ts-link { text-decoration:none; color:var(--ts-muted); padding:.4rem .7rem;
  border-radius:10px; border:1px solid transparent; }
.ts-link:hover{ border-color:rgba(148,163,184,.25); color:var(--ts-text); }

/* HERO */
.ts-hero{
  background:
    radial-gradient(1200px 520px at -10% -10%, rgba(34,211,238,.10), transparent 60%),
    radial-gradient(1100px 560px at 120% -20%, rgba(34,197,94,.12), transparent 60%),
    linear-gradient(180deg, rgba(11,19,32,.9), rgba(11,19,32,.55));
  padding: 22px 26px;
  border-radius: 18px;
  border: 1px solid rgba(148,163,184,.15);
}

/* KPIs */
.ts-kpi{
  background: linear-gradient(180deg, rgba(17,24,39,.6), rgba(17,24,39,.35));
  border: 1px solid rgba(148,163,184,.12);
  backdrop-filter: blur(6px);
  border-radius: 16px; padding: 16px 18px;
}

/* badge */
.ts-badge{
  display:inline-flex;align-items:center;gap:.45rem;
  padding:.35rem .7rem;border-radius:999px;
  border:1px solid rgba(148,163,184,.25);
  color: var(--ts-muted);font-size:.78rem;
}
.ts-dot{width:.55rem;height:.55rem;border-radius:50%;}
.ts-dot.green{background:var(--ts-green)}

/* GRID */
.grid{ display:grid; gap:14px; grid-template-columns: repeat(12, 1fr); }
.card{
  grid-column: span 3 / span 3;
  background: linear-gradient(180deg, rgba(10,17,28,.6), rgba(10,17,28,.32));
  border: 1px solid rgba(148,163,184,.12);
  border-radius:16px; padding:18px 16px; transition: transform .15s ease, border .15s ease;
}
.card:hover{ transform: translateY(-2px); border-color: rgba(34,197,94,.35); }
.card h4{ margin:0 0 6px 0; font-weight:800; letter-spacing:-.01em;}
.card p { margin:.3rem 0 0 0; color:var(--ts-muted); font-size:.94rem;}

/* SECTION TITLE */
.section-title{ display:flex; align-items:center; gap:.6rem; font-weight:800; letter-spacing:-.01em; }

/* CTA */
.cta-wrap { display:flex; gap:12px; flex-wrap:wrap; }
.btn{
  display:inline-flex; align-items:center; gap:.55rem;
  padding:.70rem 1rem; border-radius:12px; font-weight:800;
  border:1px solid rgba(148,163,184,.22); text-decoration:none; transition: all .15s ease;
}
.btn.primary{ background:var(--ts-green); color:#04110a; border-color:transparent; }
.btn.primary:hover{ background:var(--ts-green-600);}
.btn.ghost{ background:transparent; color:var(--ts-text); }
.btn.ghost:hover{ border-color:rgba(148,163,184,.35); }

/* STRIP */
.strip{
  background: linear-gradient(90deg, rgba(34,197,94,.12), rgba(59,130,246,.1));
  border: 1px solid rgba(148,163,184,.14);
  border-radius: 14px; padding: 12px 14px;
}

/* FOOTER */
.footer{
  margin-top: 30px; padding: 18px;
  border-top:1px solid rgba(148,163,184,.18);
  color: var(--ts-muted);
}
hr{border-color:rgba(148,163,184,.16);}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# PROD x DEV (secrets)
# ----------------------------------------------------------------------
ENV_MODE = st.secrets.get("env", {}).get("MODE", "prod")  # "prod" | "dev"
API_CFG   = st.secrets.get("api", {})
BACKEND_URL = (API_CFG.get("API_BASE_URL_PROD") if ENV_MODE == "prod"
               else API_CFG.get("API_BASE_URL_DEV")).rstrip("/")

def api_url(path: str) -> str:
    return f"{BACKEND_URL}{path}"

# --------------------- brand paths ---------------------
BRAND_DIR = "assets/brand"
def _theme_base():
    try:
        base = st.get_option("theme.base")
        return base if base in ("dark", "light") else "dark"
    except Exception:
        return "dark"

def wordmark_path():
    # fundo escuro -> wordmark claro ; fundo claro -> wordmark escuro
    return f"{BRAND_DIR}/terrasynapse-wordmark-light.svg" if _theme_base()=="dark" \
           else f"{BRAND_DIR}/terrasynapse-wordmark-dark.svg"

def hero_path():
    return f"{BRAND_DIR}/terrasynapse-hero-dark.svg"

# ----------------------------------------------------------------------
# HTTP helpers
# ----------------------------------------------------------------------
def _request(method, endpoint, json=None, token=None, timeout=15):
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

# ----------------------------------------------------------------------
# Geolocalização
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# Sessão
# ----------------------------------------------------------------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_token" not in st.session_state: st.session_state.user_token = None
if "user_data"  not in st.session_state: st.session_state.user_data  = None
if "loc" not in st.session_state:
    lat, lon, cidade, uf = geo_por_ip()
    st.session_state.loc = {"mode":"ip", "lat":lat, "lon":lon, "cidade":cidade, "uf":uf}
if "page" not in st.session_state:
    st.session_state.page = "Home"

# ----------------------------------------------------------------------
# NAV TOP (com wordmark e status)
# ----------------------------------------------------------------------
health_code, _health = _request("GET", "/health")
online_badge = '<span class="ts-badge"><span class="ts-dot green"></span> ONLINE</span>' if health_code == 200 \
               else '<span class="ts-badge" style="color:#f87171;border-color:#f87171">OFFLINE</span>'

col_top_l, col_top_r = st.columns([0.65, 0.35])
with col_top_l:
    st.markdown('<div class="ts-nav"><div class="inner">', unsafe_allow_html=True)
    st.image(wordmark_path(), width=220)
    st.markdown(f'<span class="ts-pill">{ENV_MODE.upper()} • {BACKEND_URL}</span>{online_badge}', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
with col_top_r:
    pass  # espaço

# ----------------------------------------------------------------------
# HERO (quando deslogado)
# ----------------------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("""
    <div class="ts-hero">
      <div style="display:flex;align-items:center;gap:16px;">
        <div style="font-size:28px">🌾</div>
        <div>
          <h1 style="margin:0;padding:0;font-weight:800;letter-spacing:-.02em">TerraSynapse V2.0</h1>
          <div style="color:var(--ts-muted)">Plataforma Enterprise de Monitoramento Agrícola</div>
        </div>
        <div style="margin-left:auto;display:flex;gap:.6rem;align-items:center;">
          <span class="ts-badge">Portal Executivo</span>
          """ + online_badge + """
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.image(hero_path(), use_container_width=True)

# ----------------------------------------------------------------------
# Sidebar — Portal Executivo
# ----------------------------------------------------------------------
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
                        time.sleep(0.6); st.rerun()
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
                        time.sleep(0.6); st.rerun()
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
                    st.success(f"Local: {cidade}-{uf} • {lat:.4f}, {lon:.4f}")
            elif mode == "Cidade/UF (precisa)":
                c1,c2 = st.columns(2)
                with c1: c = st.text_input("Cidade", value="Capinópolis")
                with c2: u = st.selectbox("UF", ["MG","SP","GO","MT","MS","PR","RS","SC","BA","TO","MA","PI","CE",
                                                 "RN","PB","PE","AL","SE","ES","RJ","AC","RO","AM","RR","PA","AP","DF"], index=0)
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

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.update({"logged_in": False, "user_token": None, "user_data": None})
            st.rerun()

        st.divider()
        if st.button("🔧 Diagnóstico do Sistema", use_container_width=True):
            code, health = _request("GET", "/health")
            if code == 200: st.success("✅ APIs TerraSynapse Online"); st.json(health)
            else:           st.error("❌ Sistema Temporariamente Indisponível")

# ----------------------------------------------------------------------
# Funções de página (páginas “reais” dentro do mesmo main)
# ----------------------------------------------------------------------
def page_home():
    st.markdown("### TerraSynapse V2.0 Enterprise  ")
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

    st.markdown("---")
    st.markdown('<div class="section-title">✨ Por que o TerraSynapse?</div>', unsafe_allow_html=True)
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

    st.markdown("---")
    st.markdown('<div class="strip">Crie sua conta executiva e tenha um cockpit unificado de clima, vegetação e mercado — pronto para decisão.</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="cta-wrap" style="margin-top:10px">'
        '<a class="btn primary" href="#portal-executivo">🚀 Entrar no Portal</a>'
        '<a class="btn ghost" href="mailto:contato@terrasynapse.com">📩 Falar com Comercial</a>'
        '</div>', unsafe_allow_html=True
    )

def page_clima():
    lat = st.session_state.loc["lat"]; lon = st.session_state.loc["lon"]
    st.subheader("🌡️ Climatologia de Precisão")
    code, res = _request("GET", f"/weather/{lat}/{lon}", token=st.session_state.user_token)
    if code == 200 and isinstance(res, dict) and res.get("status") == "success":
        clima = res["data"]
        col1,col2,col3,col4 = st.columns(4)
        with col1: st.metric("Temperatura", f"{clima['temperatura']}°C")
        with col2: st.metric("Umidade", f"{clima['umidade']}%")
        with col3: st.metric("Vento", f"{clima['vento']} km/h")
        with col4: st.metric("ET0", f"{clima['et0']} mm/dia", delta=("Crítico" if clima['et0']>6 else "Normal"))
        st.write(f"**Pressão:** {clima['pressao']} hPa  |  **Condição:** {clima['descricao']}")
        st.info(f"💧 Recomendação de irrigação: **{clima['recomendacao_irrigacao']}**")
        # Gauge ET0
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=clima['et0'],
            title={'text': "ET0 (mm/dia)"}, delta={'reference': 5},
            gauge={'axis': {'range': [None, 10]},
                   'bar': {'color': "#22c55e"},
                   'steps': [{'range': [0,3], 'color': "#1f2937"},
                             {'range': [3,6], 'color': "#a3a3a3"},
                             {'range': [6,10], 'color': "#ef4444"}],
                   'threshold': {'line': {'color': "#ef4444", 'width': 4}, 'thickness': .75, 'value': 6}}
        ))
        fig.update_layout(height=300, margin=dict(l=20,r=20,t=30,b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Não foi possível carregar o clima agora.")

def page_vegetacao():
    lat = st.session_state.loc["lat"]; lon = st.session_state.loc["lon"]
    st.subheader("🛰️ NDVI Executivo")
    code, res = _request("GET", f"/satellite/{lat}/{lon}", token=st.session_state.user_token)
    if code == 200 and isinstance(res, dict) and res.get("status") == "success":
        ndvi = res["data"]
        c1,c2,c3 = st.columns(3)
        with c1: st.metric("NDVI", ndvi["ndvi"])
        with c2: st.metric("Status", ndvi["status_vegetacao"])
        with c3: st.metric("Data", ndvi["data_analise"])
        st.info(ndvi["recomendacao"])
    else:
        st.error("Não foi possível carregar o NDVI agora.")

def page_mercado():
    st.subheader("📈 Mercado em Tempo Real")
    code, res = _request("GET", "/market", token=st.session_state.user_token)
    if code == 200 and isinstance(res, dict) and res.get("status") == "success":
        com = res["data"]
        df = pd.DataFrame([
            {"Commodity":"Soja","Preço (R$/saca)":com["soja"]["preco"], "Variação %": com["soja"].get("variacao",0.0)},
            {"Commodity":"Milho","Preço (R$/saca)":com["milho"]["preco"], "Variação %": com["milho"].get("variacao",0.0)},
            {"Commodity":"Café","Preço (R$/saca)":com["cafe"]["preco"], "Variação %": com["cafe"].get("variacao",0.0)},
        ])
        colA, colB = st.columns([1,1])
        with colA:
            st.dataframe(df, use_container_width=True, hide_index=True)
        with colB:
            fig = px.bar(df, x="Commodity", y="Preço (R$/saca)")
            fig.update_layout(height=320, margin=dict(l=20,r=20,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Não foi possível carregar o mercado agora.")

def page_rentabilidade():
    st.subheader("🤖 IA de Rentabilidade")
    # Preços do mercado para cálculo
    code, res = _request("GET", "/market", token=st.session_state.user_token)
    if code == 200 and isinstance(res, dict) and res.get("status") == "success":
        com = res["data"]
    else:
        st.warning("Sem mercado agora; usando preços padrão.")
        com = {"soja":{"preco":165.0},"milho":{"preco":75.0},"cafe":{"preco":950.0}}

    c1, c2, c3 = st.columns(3)
    with c1: area = st.number_input("🌾 Área (hectares)", min_value=1, value=10)
    with c2: cultura = st.selectbox("🌱 Cultura Principal", ["Soja","Milho","Café"])
    with c3: prod = st.number_input("📊 Produtividade (sacas/ha)", min_value=1, value=50)
    preco = com[cultura.lower()]["preco"]
    receita_total = area * prod * preco
    custo_total   = area * 3000
    lucro_total   = receita_total - custo_total
    margem = (lucro_total/receita_total*100) if receita_total else 0
    m1,m2,m3 = st.columns(3)
    with m1: st.metric("Receita Total", f"R$ {receita_total:,.0f}")
    with m2: st.metric("Custo Estimado", f"R$ {custo_total:,.0f}")
    with m3: st.metric("Lucro Projetado", f"R$ {lucro_total:,.0f}")
    st.caption(f"**Área:** {area} ha | **Produtividade:** {prod} sc/ha | **Preço:** R$ {preco}/saca | **Margem:** {margem:.1f}%")

# ----------------------------------------------------------------------
# Navegação de páginas
# ----------------------------------------------------------------------
if st.session_state.logged_in:
    # Segmented nav simples para páginas
    st.session_state.page = st.segmented_control(
        "Navegação",
        options=["Home","Clima","Vegetação","Mercado","Rentabilidade"],
        default=st.session_state.page,
        help="Troque a página sem perder o contexto.",
    )

    if st.session_state.page == "Home":
        page_home()
    elif st.session_state.page == "Clima":
        page_clima()
    elif st.session_state.page == "Vegetação":
        page_vegetacao()
    elif st.session_state.page == "Mercado":
        page_mercado()
    else:
        page_rentabilidade()
else:
    # Landing enterprise (deslogado)
    page_home()

# ----------------------------------------------------------------------
# Rodapé (sempre)
# ----------------------------------------------------------------------
st.markdown('<div id="portal-executivo"></div>', unsafe_allow_html=True)
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
