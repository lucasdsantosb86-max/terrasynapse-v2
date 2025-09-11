# TerraSynapse - Frontend Enterprise (Streamlit)
# Navegação única por view (Dashboard/Clima/Vegetação/Mercado/Rentabilidade)
# Patch incremental: cache/UX, login premium, sinais agronômicos, tendência de risco,
# checklist DEV/PROD, correção deprecation (use_container_width), sem regressões.

import streamlit as st
import requests
import time
from datetime import datetime
import math
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ----------------------------------------------------------------------
# Configuração base (deve ser a 1ª chamada st.*)
# ----------------------------------------------------------------------
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

/* TOP BAR + NAV */
.ts-top { display:flex; align-items:center; gap:.6rem; flex-wrap:wrap; margin-bottom:.25rem; }
.ts-pill {
  border:1px solid rgba(148,163,184,.25); border-radius:999px; padding:.35rem .7rem;
  color:var(--ts-muted); font-size:.82rem;
}
.ts-badge{
  display:inline-flex;align-items:center;gap:.45rem;
  padding:.35rem .7rem;border-radius:999px;
  border:1px solid rgba(148,163,184,.25);
  color: var(--ts-muted);font-size:.78rem;
}
.ts-dot{width:.55rem;height:.55rem;border-radius:50%;}
.ts-dot.green{background:var(--ts-green)}
.navbar{ display:flex; gap:.35rem; flex-wrap:wrap; margin-left:auto; }
div.stButton > button.ts-tab {
  background: transparent; border:1px solid rgba(148,163,184,.22);
  color: var(--ts-muted); padding:.42rem .75rem; border-radius:10px; font-weight:700;
}
div.stButton > button.ts-tab:hover { border-color:rgba(148,163,184,.35); color:var(--ts-text); }
div.stButton > button.ts-tab.active { background: var(--ts-green); color:#04110a; border-color:transparent; }

/* HERO (somente na home deslogada) */
.ts-hero{
  background:
    radial-gradient(1200px 520px at -10% -10%, rgba(34,211,238,.10), transparent 60%),
    radial-gradient(1100px 560px at 120% -20%, rgba(34,197,94,.12), transparent 60%),
    linear-gradient(180deg, rgba(11,19,32,.9), rgba(11,19,32,.55));
  padding: 12px 16px 6px 16px;
  border-radius: 18px;
  border: 1px solid rgba(148,163,184,.15);
  overflow:hidden;
}
.ts-hero img { width:100%; height:auto; display:block; }

/* KPIs & CARDS */
.ts-kpi{
  background: linear-gradient(180deg, rgba(17,24,39,.6), rgba(17,24,39,.35));
  border: 1px solid rgba(148,163,184,.12);
  backdrop-filter: blur(6px);
  border-radius: 16px; padding: 16px 18px;
}
.grid{ display:grid; gap:14px; grid-template-columns: repeat(12, 1fr); }
.card{
  grid-column: span 12 / span 12;
  background: linear-gradient(180deg, rgba(10,17,28,.6), rgba(10,17,28,.32));
  border: 1px solid rgba(148,163,184,.12);
  border-radius:16px; padding:18px 16px; transition: transform .15s ease, border .15s ease;
}
@media (min-width: 992px){ .card{ grid-column: span 6 / span 6; } }
.card:hover{ transform: translateY(-2px); border-color: rgba(34,197,94,.35); }
.card h4{ margin:0 0 6px 0; font-weight:800; letter-spacing:-.01em;}
.card p { margin:.3rem 0 0 0; color:var(--ts-muted); font-size:.94rem;}

/* SECTION TITLE + STRIP + FOOTER */
.section-title{ display:flex; align-items:center; gap:.6rem; font-weight:800; letter-spacing:-.01em; }
.strip{
  background: linear-gradient(90deg, rgba(34,197,94,.12), rgba(59,130,246,.1));
  border: 1px solid rgba(148,163,184,.14);
  border-radius: 14px; padding: 12px 14px;
}
.footer{
  margin-top: 30px; padding: 18px;
  border-top:1px solid rgba(148,163,184,.18);
  color: var(--ts-muted);
}
hr{border-color:rgba(148,163,184,.16);}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# DEV/PROD por secrets
# ----------------------------------------------------------------------
ENV_MODE = st.secrets.get("env", {}).get("MODE", "prod")  # "prod" | "dev"
API_CFG   = st.secrets.get("api", {})
BACKEND_URL = (API_CFG.get("API_BASE_URL_PROD") if ENV_MODE == "prod"
               else API_CFG.get("API_BASE_URL_DEV", API_CFG.get("API_BASE_URL_PROD",""))).rstrip("/")

def api_url(path: str) -> str:
    return f"{BACKEND_URL}{path}"

# ----------------------------------------------------------------------
# HTTP helpers (com reuso de conexão) + cache leve
# ----------------------------------------------------------------------
_session = requests.Session()
_adapter = requests.adapters.HTTPAdapter(pool_connections=8, pool_maxsize=8, max_retries=1)
_session.mount("http://", _adapter)
_session.mount("https://", _adapter)

def api_request(method, endpoint, json=None, token=None, timeout=15):
    """Helper de requisições (GET/POST). Retorna (status_code, body)."""
    url = api_url(endpoint)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        if method == "GET":
            r = _session.get(url, headers=headers, timeout=timeout)
        else:
            r = _session.post(url, headers=headers, json=json, timeout=timeout)
        try:
            body = r.json()
        except Exception:
            body = r.text
        return r.status_code, body
    except requests.exceptions.RequestException as e:
        return 0, {"detail": f"connection_error: {e}"}

@st.cache_data(ttl=60, show_spinner=False)
def cached_health():
    return api_request("GET", "/health")

@st.cache_data(ttl=45, show_spinner=False)
def cached_dashboard(lat: float, lon: float, token: str|None):
    return api_request("GET", f"/dashboard/{lat}/{lon}", token=token)

# ----------------------------------------------------------------------
# Geolocalização
# ----------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def geo_por_ip():
    try:
        r = _session.get("https://ipapi.co/json/", timeout=8)
        if r.status_code == 200:
            d = r.json()
            return float(d["latitude"]), float(d["longitude"]), d.get("city",""), d.get("region","")
    except Exception:
        pass
    g = st.secrets.get("geo", {})
    return float(g.get("DEFAULT_LAT", -15.78)), float(g.get("DEFAULT_LON", -47.93)), \
           g.get("DEFAULT_CITY","Brasília"), g.get("DEFAULT_STATE","DF")

@st.cache_data(ttl=24*3600, show_spinner=False)
def geocode_openweather(cidade:str, uf:str):
    key = st.secrets.get("openweather", {}).get("API_KEY", "")
    if not key:
        return None
    try:
        url = "https://api.openweathermap.org/geo/1.0/direct"
        params = {"q": f"{cidade},{uf},BR", "limit": 1, "appid": key}
        r = _session.get(url, params=params, timeout=10)
        if r.status_code == 200 and isinstance(r.json(), list) and r.json():
            d = r.json()[0]
            return float(d["lat"]), float(d["lon"])
    except Exception:
        pass
    return None

# ----------------------------------------------------------------------
# Sessão + query param inicial
# ----------------------------------------------------------------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_token" not in st.session_state: st.session_state.user_token = None
if "user_data"  not in st.session_state: st.session_state.user_data  = {}
if "loc" not in st.session_state:
    lat, lon, cidade, uf = geo_por_ip()
    st.session_state.loc = {"mode":"ip", "lat":lat, "lon":lon, "cidade":cidade, "uf":uf}
if "view" not in st.session_state:
    # respeita ?view=... (dashboard|clima|vegetacao|mercado|rent)
    try:
        qp = st.query_params
        if "view" in qp:
            st.session_state.view = qp.get("view")
        else:
            st.session_state.view = "dashboard"
    except Exception:
        st.session_state.view = st.experimental_get_query_params().get("view", ["dashboard"])[0]
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False
if "trend" not in st.session_state:
    st.session_state.trend = {"et0": [], "ndvi": [], "ts": []}

# ----------------------------------------------------------------------
# Métricas derivadas (sinais agronômicos)
# ----------------------------------------------------------------------
def heat_index_c(temp_c: float, rh: float) -> float:
    """Índice de calor (Rothfusz) aproximado. Retorna em °C."""
    # Válido para T > ~26°C e RH > 40%. Caso contrário, retorna T.
    if temp_c < 26 or rh < 40:
        return temp_c
    T = temp_c * 9/5 + 32
    R = rh
    HI = (-42.379 + 2.04901523*T + 10.14333127*R
          - 0.22475541*T*R - 6.83783e-3*T*T - 5.481717e-2*R*R
          + 1.22874e-3*T*T*R + 8.5282e-4*T*R*R - 1.99e-6*T*T*R*R)
    # Ajustes empíricos
    if R < 13 and 80 <= T <= 112:
        HI -= ((13 - R)/4)*math.sqrt((17 - abs(T-95.))/17)
    if R > 85 and 80 <= T <= 87:
        HI += 0.02*(R-85)*(87-T)
    return (HI - 32) * 5/9

def vpd_kpa(temp_c: float, rh: float) -> float:
    """Déficit de pressão de vapor (kPa) ~ conforto 0.8–1.2; alto >2.0."""
    es = 0.6108 * math.exp((17.27*temp_c)/(temp_c+237.3))
    return es * (1 - rh/100)

def thi_cattle(temp_c: float, rh: float) -> float:
    """THI bovino (°C): quanto maior, mais estresse térmico."""
    return temp_c - (0.55 - 0.0055*rh)*(temp_c - 14.5)

def class_heat_index(hi_c: float) -> str:
    if hi_c >= 41: return "Perigo extremo"
    if hi_c >= 32: return "Perigo"
    if hi_c >= 27: return "Alerta"
    return "Conforto"

def class_vpd(vpd: float) -> str:
    if vpd >= 2.0: return "Estresse hídrico"
    if vpd >= 1.2: return "Alto"
    if vpd >= 0.8: return "Ideal"
    if vpd >= 0.4: return "Baixo (risco doença)"
    return "Muito baixo"

def class_thi(thi: float) -> str:
    if thi >= 78: return "Severo"
    if thi >= 74: return "Alto"
    if thi >= 70: return "Moderado"
    return "Conforto"

# ----------------------------------------------------------------------
# Top bar: status + nav (sem abrir nova aba)
# ----------------------------------------------------------------------
health_code, _health = cached_health()
online_badge = ('<span class="ts-badge"><span class="ts-dot green"></span> ONLINE</span>'
                if health_code == 200 else
                '<span class="ts-badge" style="color:#f87171;border-color:#f87171">OFFLINE</span>')

def topbar_and_nav():
    st.markdown(
        f'<div class="ts-top">'
        f'<span class="ts-pill">{ENV_MODE.upper()} • {BACKEND_URL}</span>'
        f'{online_badge}'
        f'</div>', unsafe_allow_html=True
    )
    with st.container():
        cols = st.columns(5)
        labels = [("dashboard","Dashboard"), ("clima","Clima"), ("vegetacao","Vegetação"),
                  ("mercado","Mercado"), ("rent","Rentabilidade")]
        for i,(key,label) in enumerate(labels):
            active = "active" if st.session_state.view == key else ""
            if cols[i].button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.view = key
                try: st.query_params.update({"view": key})
                except Exception: st.experimental_set_query_params(view=key)
                st.rerun()
            # Estilo dos botões
            st.markdown("""
                <style>
                  div.stButton > button {padding:.42rem .75rem; border-radius:10px;}
                </style>
            """, unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Sidebar — Portal Executivo (com checklist DEV/PROD)
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("🔐 Portal Executivo")

    # Mensagem institucional para não logado (login premium curto)
    if not st.session_state.logged_in:
        st.info(
            "Bem-vindo ao **TerraSynapse** — Plataforma Enterprise de Inteligência Agrícola.\n\n"
            "Crie sua conta para acessar **clima**, **NDVI**, **mercado** e **rentabilidade** em tempo real."
        )
        st.caption("📞 WhatsApp: **(34) 99972-9740**  •  📧 **terrasynapse@terrasynapse.com**")

    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["🔑 Login", "👤 Cadastro"])

        with tab1:
            email = st.text_input("📧 Email Corporativo", key="login_email")
            password = st.text_input("🔒 Senha", type="password", key="login_password")
            if st.button("🚀 Entrar", type="primary", use_container_width=True):
                if email and password:
                    with st.spinner("Autenticando..."):
                        code, body = api_request("POST", "/login", json={"email": email, "password": password})
                    if code == 200 and isinstance(body, dict) and "access_token" in body:
                        st.session_state.logged_in = True
                        st.session_state.user_token = body["access_token"]
                        st.session_state.user_data = body.get("user", {})
                        st.success("✅ Login realizado com sucesso!")
                        time.sleep(0.5); st.rerun()
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
            estados = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA",
                       "PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
            uf_idx = estados.index(st.secrets.get("geo",{}).get("DEFAULT_STATE","MG")) \
                        if st.secrets.get("geo",{}).get("DEFAULT_STATE","MG") in estados else 0
            estado  = st.selectbox("📍 Estado", estados, index=uf_idx)
            if st.button("🎯 Criar Conta Enterprise", type="primary", use_container_width=True):
                if nome and email_reg and password_reg:
                    payload = {
                        "nome_completo": nome, "email": email_reg, "password": password_reg,
                        "perfil_profissional": perfil, "empresa_propriedade": empresa,
                        "cidade": cidade, "estado": estado
                    }
                    with st.spinner("Criando sua conta..."):
                        code, body = api_request("POST", "/register", json=payload)
                    if code == 200 and isinstance(body, dict) and "access_token" in body:
                        st.session_state.logged_in = True
                        st.session_state.user_token = body["access_token"]
                        st.session_state.user_data = body.get("user", {})
                        st.success("✅ Conta criada com sucesso!")
                        time.sleep(0.5); st.rerun()
                    else:
                        st.error("❌ Erro no cadastro")
                else:
                    st.warning("⚠️ Preencha os obrigatórios")
    else:
        nome_exib = st.session_state.user_data.get("nome") or st.session_state.user_data.get("nome_completo") or "Usuário"
        st.success(f"👋 Bem-vindo, {nome_exib}!")
        with st.expander("📍 Local de Trabalho", expanded=True):
            mode = st.radio("Modo", ["Automática (IP)", "Cidade/UF (precisa)", "Coordenadas"], horizontal=False)
            if mode == "Automática (IP)":
                if st.button("Detectar por IP", use_container_width=True):
                    lat, lon, cidade, uf = geo_por_ip()
                    st.session_state.loc.update({"mode":"ip","lat":lat,"lon":lon,"cidade":cidade,"uf":uf})
                    st.success(f"Local: {cidade}-{uf} • {lat:.4f}, {lon:.4f}")
            elif mode == "Cidade/UF (precisa)":
                c1,c2 = st.columns(2)
                with c1: c = st.text_input("Cidade", value=st.session_state.loc.get("cidade",""))
                with c2:
                    estados = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT","PA",
                               "PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
                    default_uf = st.session_state.loc.get("uf","MG")
                    idx = estados.index(default_uf) if default_uf in estados else 12
                    u = st.selectbox("UF", estados, index=idx)
                if st.button("📡 Buscar Coordenadas (OpenWeather)", use_container_width=True):
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
                if st.button("Usar estas coordenadas", use_container_width=True):
                    st.session_state.loc.update({"mode":"manual","lat":lat,"lon":lon})
                    st.success(f"Local setado • {lat:.4f}, {lon:.4f}")

        st.checkbox("⚡ Auto-refresh a cada 45s", key="auto_refresh")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.update({"logged_in": False, "user_token": None, "user_data": {}})
            st.rerun()

    st.divider()
    if st.button("🔧 Diagnóstico do Sistema", use_container_width=True):
        code, health = api_request("GET", "/health")
        if code == 200: st.success("✅ APIs TerraSynapse Online"); st.json(health)
        else:           st.error("❌ Sistema Temporariamente Indisponível")

    with st.expander("🧪 Ambiente & Deploy (checklist rápido)", expanded=False):
        ok_api = bool(BACKEND_URL)
        ok_mode = ENV_MODE in ("prod","dev")
        ok_geo = "DEFAULT_LAT" in st.secrets.get("geo",{}) and "DEFAULT_LON" in st.secrets.get("geo",{})
        ok_ow  = bool(st.secrets.get("openweather",{}).get("API_KEY",""))
        st.write(f"• MODE: **{ENV_MODE}** {'✅' if ok_mode else '❌'}")
        st.write(f"• Backend URL: **{BACKEND_URL}** {'✅' if ok_api else '❌'}")
        st.write(f"• OpenWeather API_KEY {'✅' if ok_ow else '❌'}")
        st.write(f"• Geo defaults (lat/lon) {'✅' if ok_geo else '❌'}")
        st.caption("Dica: secrets.toml → [env],[api],[geo],[openweather],[admin]")

# ----------------------------------------------------------------------
# Util: alerta prático (com base no dashboard do backend)
# ----------------------------------------------------------------------
def avaliar_alertas(d):
    """Gera lista de alertas a partir do payload de dashboard."""
    if not d or "clima" not in d or "vegetacao" not in d:
        return []
    clima = d["clima"]
    ndvi  = d["vegetacao"]
    t = float(clima.get("temperatura", 0))
    u = float(clima.get("umidade", 0))
    v = float(clima.get("vento", 0))
    et0 = float(clima.get("et0", 0))
    descr = str(clima.get("descricao","")).lower()
    chuva_mm = 0.0  # placeholder para futuro

    alertas = []

    # Risco de calor/seca/vento (queimadas)
    if t >= 35 and u <= 25 and v >= 8:
        alertas.append(("alta", "🔥 Risco de queimadas elevado (calor + baixa umidade + vento). Reforçar vigilância e evitar fogo."))
    elif t >= 33 and u <= 30:
        alertas.append(("media", "🌡️ Calor e secura — considerar manejo de poeira e hidratação da equipe."))

    # Ventos fortes
    if v >= 35:
        alertas.append(("alta", "💨 Ventos fortes — risco para pulverização e estruturas expostas."))

    # Chuva forte (placeholder)
    if chuva_mm >= 20:
        alertas.append(("media", "🌧️ Chuva forte nas próximas horas — ajustar cronograma de colheita/aplicação."))

    # Irrigação via ET0
    if et0 > 6:
        alertas.append(("alta", f"💧 ET0 elevada ({et0} mm/dia) — irrigação fortemente recomendada."))
    elif et0 > 4:
        alertas.append(("media", f"💧 ET0 moderada ({et0} mm/dia) — monitorar necessidade de irrigação."))

    # Vegetação
    if float(ndvi.get("ndvi", 0)) < 0.5:
        alertas.append(("media", f"🌱 NDVI baixo ({ndvi.get('ndvi')}) — verificar pragas/doenças."))

    # Condição textual (poeira/fumaça)
    if "smoke" in descr or "poeira" in descr or "haze" in descr:
        alertas.append(("media", "🏞️ Qualidade do ar ruim — considerar manejo de poeira/fumaça."))

    return alertas

# ----------------------------------------------------------------------
# Trend skeleton (pré-preditivo) — guarda últimas amostras da sessão
# ----------------------------------------------------------------------
def push_trend_samples(et0_val: float, ndvi_val: float):
    ts = datetime.utcnow().timestamp()
    st.session_state.trend["et0"].append(float(et0_val))
    st.session_state.trend["ndvi"].append(float(ndvi_val))
    st.session_state.trend["ts"].append(ts)
    # mantém somente últimas 12 amostras
    for k in ("et0","ndvi","ts"):
        st.session_state.trend[k] = st.session_state.trend[k][-12:]

def calc_trend_label():
    et0 = st.session_state.trend["et0"]
    ndv = st.session_state.trend["ndvi"]
    if len(et0) < 4 or len(ndv) < 4:
        return "Tendência: coletando dados…"
    # slope simples: último - média dos anteriores
    et0_slope = et0[-1] - sum(et0[:-1])/len(et0[:-1])
    ndvi_slope = ndv[-1] - sum(ndv[:-1])/len(ndv[:-1])
    if et0_slope > 0.3 and ndvi_slope < -0.02:
        return "Tendência de risco hídrico ↑ (48h)"
    if et0_slope > 0.2:
        return "ET0 em alta (monitorar irrigação)"
    if ndvi_slope < -0.02:
        return "NDVI em queda (verificar campo)"
    return "Tendência estável"

# ----------------------------------------------------------------------
# Seções (conteúdo)
# ----------------------------------------------------------------------
def page_dashboard():
    lat = st.session_state.loc["lat"]; lon = st.session_state.loc["lon"]
    st.markdown(
        f'<div class="ts-top"><span class="ts-pill">Local: {st.session_state.loc.get("cidade","")}'
        f' - {st.session_state.loc.get("uf","")} • {lat:.4f}, {lon:.4f}</span>{online_badge}</div>',
        unsafe_allow_html=True
    )

    colA, colB = st.columns([1,1])
    with colA:
        if st.button("🔄 Atualizar Dados", type="primary", use_container_width=True):
            st.cache_data.clear(); st.rerun()
    with colB:
        if st.session_state.auto_refresh:
            st.caption("⏱️ Atualizando a cada 45s…")
            time.sleep(45); st.cache_data.clear(); st.rerun()

    st.markdown("---")

    with st.spinner("Carregando dashboard…"):
        code, dash = cached_dashboard(lat, lon, st.session_state.user_token)

    if code == 200 and isinstance(dash, dict) and dash.get("status") == "success":
        data = dash["data"]

        # KPIs principais
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
            st.metric("🌱 NDVI", f"{data['vegetacao']['ndvi']}",
                      delta=data['vegetacao']['status_vegetacao'])
            st.markdown('</div>', unsafe_allow_html=True)
        with k4:
            st.markdown('<div class="ts-kpi">', unsafe_allow_html=True)
            rec = data['rentabilidade']['receita_por_hectare']
            st.metric("💰 Receita/ha", f"R$ {rec:,.0f}",
                      delta=f"{data['rentabilidade']['produtividade_estimada']} sc/ha")
            st.markdown('</div>', unsafe_allow_html=True)

        # Tendência (pré-preditivo, em cima de amostras da sessão)
        push_trend_samples(data['clima']['et0'], data['vegetacao']['ndvi'])
        st.markdown("##### 🔮 Tendência de Risco (esqueleto)")
        st.info(calc_trend_label())

        st.markdown("---")
        st.markdown('#### ⚠️ Centro de Alertas Inteligentes')
        alerts = avaliar_alertas(data)
        if alerts:
            for pri,msg in alerts:
                (st.error if pri=="alta" else st.warning)(msg)
        else:
            st.success("✅ SISTEMA OPERACIONAL: Nenhum alerta crítico detectado.")

    else:
        st.error("❌ Não foi possível carregar o dashboard. Verifique o login e tente novamente.")

def page_clima():
    lat = st.session_state.loc["lat"]; lon = st.session_state.loc["lon"]
    with st.spinner("Carregando clima…"):
        code, dash = cached_dashboard(lat, lon, st.session_state.user_token)
    if code == 200 and isinstance(dash, dict) and dash.get("status") == "success":
        data = dash["data"]; clima = data["clima"]

        # Sinais agronômicos derivados (sem tocar no backend)
        T = float(clima['temperatura']); RH = float(clima['umidade'])
        HI  = round(heat_index_c(T, RH), 1)
        VPD = round(vpd_kpa(T, RH), 2)
        THI = round(thi_cattle(T, RH), 1)

        st.subheader("🌤️ Climatologia de Precisão")
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: st.write(f"**Temperatura:** {clima['temperatura']}°C")
        with c2: st.write(f"**Umidade:** {clima['umidade']}%")
        with c3: st.write(f"**Vento:** {clima['vento']} km/h")
        with c4: st.write(f"**Pressão:** {clima['pressao']} hPa")
        with c5: st.write(f"**Condição:** {clima['descricao']}")

        # KPIs de sinais
        k1,k2,k3 = st.columns(3)
        with k1:
            st.markdown('<div class="ts-kpi">', unsafe_allow_html=True)
            st.metric("🌡️ Heat Index (°C)", HI, delta=class_heat_index(HI))
            st.caption("Sensação de calor combinando T e UR.")
            st.markdown('</div>', unsafe_allow_html=True)
        with k2:
            st.markdown('<div class="ts-kpi">', unsafe_allow_html=True)
            st.metric("💨 VPD (kPa)", VPD, delta=class_vpd(VPD))
            st.caption("0.8–1.2 ideal; >2.0 estresse hídrico.")
            st.markdown('</div>', unsafe_allow_html=True)
        with k3:
            st.markdown('<div class="ts-kpi">', unsafe_allow_html=True)
            st.metric("🐄 THI (bovino)", THI, delta=class_thi(THI))
            st.caption("Conforto térmico pecuária.")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("##### 💧 Evapotranspiração (ET0)")
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
        fig.update_layout(height=320, margin=dict(l=20,r=20,t=20,b=10))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### 🧭 Recomendação")
        st.info(f"Irrigação: **{clima['recomendacao_irrigacao']}**")
    else:
        st.error("❌ Não foi possível carregar o clima agora.")

def page_vegetacao():
    lat = st.session_state.loc["lat"]; lon = st.session_state.loc["lon"]
    with st.spinner("Carregando NDVI…"):
        code, dash = cached_dashboard(lat, lon, st.session_state.user_token)
    if code == 200 and isinstance(dash, dict) and dash.get("status") == "success":
        v = dash["data"]["vegetacao"]
        st.subheader("🛰️ NDVI Executivo")
        c1,c2,c3 = st.columns(3)
        with c1: st.write(f"**Valor:** {v['ndvi']}")
        with c2: st.write(f"**Status:** {v['status_vegetacao']}")
        with c3: st.write(f"**Data:** {v['data_analise']}")
        st.markdown("##### 📋 Recomendações Técnicas")
        st.info(v['recomendacao'])
    else:
        st.error("❌ Não foi possível carregar o NDVI agora.")

def page_mercado():
    lat = st.session_state.loc["lat"]; lon = st.session_state.loc["lon"]
    with st.spinner("Carregando mercado…"):
        code, dash = cached_dashboard(lat, lon, st.session_state.user_token)
    if code == 200 and isinstance(dash, dict) and dash.get("status") == "success":
        com = dash["data"]["mercado"]
        st.subheader("📈 Mercado em Tempo Real (R$/saca)")
        df = pd.DataFrame([
            {"Commodity":"Soja","Preço":com["soja"]["preco"]},
            {"Commodity":"Milho","Preço":com["milho"]["preco"]},
            {"Commodity":"Café","Preço":com["cafe"]["preco"]}
        ])
        figb = px.bar(df, x="Commodity", y="Preço", title=None)
        figb.update_layout(height=420, margin=dict(l=20,r=20,t=10,b=10))
        st.plotly_chart(figb, use_container_width=True)
        st.caption("Fonte: Yahoo Finance + Exchangerate.host (conversão USD/BRL).")
    else:
        st.error("❌ Não foi possível carregar o mercado agora.")

def page_rent():
    lat = st.session_state.loc["lat"]; lon = st.session_state.loc["lon"]
    with st.spinner("Carregando rentabilidade…"):
        code, dash = cached_dashboard(lat, lon, st.session_state.user_token)
    if code == 200 and isinstance(dash, dict) and dash.get("status") == "success":
        data = dash["data"]; mercado = data["mercado"]

        st.subheader("🧮 IA de Rentabilidade")
        c1, c2, c3 = st.columns(3)
        with c1: area = st.number_input("🌾 Área (hectares)", min_value=1, value=10)
        with c2: cultura = st.selectbox("🌱 Cultura Principal", ["Soja","Milho","Café"])
        with c3: prod = st.number_input("📊 Produtividade (sacas/ha)", min_value=1, value=data['rentabilidade']['produtividade_estimada'])

        if cultura.lower() in mercado:
            preco = mercado[cultura.lower()]['preco']
            receita_total = area * prod * preco
            custo_total   = area * 3000
            lucro_total   = receita_total - custo_total
            margem = (lucro_total/receita_total*100) if receita_total else 0

            m1,m2,m3 = st.columns(3)
            with m1: st.metric("Receita Total", f"R$ {receita_total:,.0f}")
            with m2: st.metric("Custo Estimado", f"R$ {custo_total:,.0f}")
            with m3: st.metric("Lucro Projetado", f"R$ {lucro_total:,.0f}")
            st.caption(f"**Área:** {area} ha | **Produtividade:** {prod} sc/ha | **Preço:** R$ {preco}/saca | **Margem:** {margem:.1f}%")
    else:
        st.error("❌ Não foi possível carregar a rentabilidade agora.")

# ----------------------------------------------------------------------
# Renderização
# ----------------------------------------------------------------------
def home_logged_out():
    # Hero (SVG na sua pasta assets/brand/) — corrige deprecation: use_container_width
    st.markdown('<div class="ts-hero">', unsafe_allow_html=True)
    st.image("assets/brand/terrasynapse-hero-dark.svg", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### TerraSynapse V2.0 Enterprise")
    st.caption("Plataforma Líder em Inteligência Agrícola")

    c1,c2,c3,c4 = st.columns(4)
    for col, title, value in [
        (c1, "Cobertura Climática", "🔭 200k+ localidades"),
        (c2, "Atualização", "⚡ ~15s"),
        (c3, "SLA", "99.9%"),
        (c4, "Segurança", "JWT + CORS"),
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
    # CTA curto para login/cadastro (sidebar)
    st.markdown('<div class="strip"><b>Pronto para começar?</b> Abra o menu lateral, faça <i>Login</i> ou <i>Cadastro</i> e acesse o cockpit executivo.</div>', unsafe_allow_html=True)

# top bar e, se logado, navbar
if st.session_state.logged_in:
    topbar_and_nav()

# página
if st.session_state.logged_in:
    view = st.session_state.view
    if view == "dashboard":
        page_dashboard()
    elif view == "clima":
        page_clima()
    elif view == "vegetacao":
        page_vegetacao()
    elif view == "mercado":
        page_mercado()
    elif view == "rent":
        page_rent()
else:
    home_logged_out()

# ----------------------------------------------------------------------
# Rodapé
# ----------------------------------------------------------------------
st.markdown("""
<div class="footer">
  <div style="display:flex; flex-wrap:wrap; gap:10px; align-items:center;">
    <div>© TerraSynapse V2.0 — Plataforma Enterprise</div>
    <div style="margin-left:auto;">
      <a class="ts-pill" href="mailto:terrasynapse@terrasynapse.com">📩 terrasynapse@terrasynapse.com</a>
      <span class="ts-pill">📞 (34) 99972-9740</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
