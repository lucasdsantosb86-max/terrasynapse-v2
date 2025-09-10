# TerraSynapse - Frontend Enterprise (Streamlit)
# Visual Enterprise + PROD/DEV + Geolocalização (IP/OWM) + Página do Dev
# Mantém compatibilidade com /login, /register, /dashboard/{lat}/{lon}, /market

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
  --ts-ink:#0b1420;
  --ts-bg:#0F172A;
  --ts-card:#0B1320;
  --ts-outline:#1f2937;
  --ts-text:#E5E7EB;
  --ts-muted:#94A3B8;
  --ts-danger:#ef4444;
}
html, body, [class*="css"]  { font-family: 'Inter', system-ui; color: var(--ts-text); }
section.main > div { padding-top: .6rem; }

/* HERO */
.ts-hero{
  background:
    radial-gradient(1100px 480px at -10% -10%, rgba(34,211,238,.10), transparent 60%),
    radial-gradient(1000px 520px at 120% -20%, rgba(34,197,94,.12), transparent 60%),
    linear-gradient(180deg, rgba(11,19,32,.85), rgba(11,19,32,.55));
  padding: 20px 26px;
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

/* BADGE */
.ts-badge{
  display:inline-flex;align-items:center;gap:.45rem;
  padding:.35rem .7rem;border-radius:999px;
  border:1px solid rgba(148,163,184,.25);
  color: var(--ts-muted);font-size:.78rem;
}
.ts-dot{width:.55rem;height:.55rem;border-radius:50%;}
.ts-dot.green{background:var(--ts-green)}

/* GRID CARDS */
.grid{
  display:grid; gap:14px;
  grid-template-columns: repeat(12, 1fr);
}
.card{
  grid-column: span 3 / span 3;
  background: linear-gradient(180deg, rgba(10,17,28,.6), rgba(10,17,28,.3));
  border: 1px solid rgba(148,163,184,.12);
  border-radius:16px; padding:18px 16px;
}
.card h4{ margin:0 0 6px 0; font-weight:700; letter-spacing:-.01em;}
.card p { margin:.3rem 0 0 0; color:var(--ts-muted); font-size:.94rem;}

/* CTA */
.cta-wrap { display:flex; gap:12px; flex-wrap:wrap; }
.btn{
  display:inline-flex; align-items:center; gap:.55rem;
  padding:.62rem .9rem; border-radius:12px; font-weight:700;
  border:1px solid rgba(148,163,184,.2); text-decoration:none;
}
.btn.primary{ background:var(--ts-green); color:#04110a; border-color:transparent; }
.btn.ghost{ background:transparent; color:var(--ts-text); }
hr{border-color:rgba(148,163,184,.16);}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# PROD x DEV: lido do secrets (não mexe em produção)
# ----------------------------------------------------------------------
ENV_MODE = st.secrets.get("env", {}).get("MODE", "prod")  # "prod" | "dev"
API_CFG   = st.secrets.get("api", {})
BACKEND_URL = (API_CFG.get("API_BASE_URL_PROD") if ENV_MODE == "prod"
               else API_CFG.get("API_BASE_URL_DEV")).rstrip("/")

def api_url(path: str) -> str:
    return f"{BACKEND_URL}{path}"

# ----------------------------------------------------------------------
# HTTP helpers (endpoints protegidos exigem token)
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
    """Rápida por IP (default)."""
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
    """Precisa por Cidade/UF — usa OpenWeather Geocoding."""
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

# ----------------------------------------------------------------------
# Header (Hero Enterprise)
# ----------------------------------------------------------------------
# Status do backend (rapidinho — não bloqueia se cair)
health_code, _health = _request("GET", "/health")
online_badge = '<span class="ts-badge"><span class="ts-dot green"></span> ONLINE</span>' if health_code == 200 \
               else '<span class="ts-badge" style="color:#f87171;border-color:#f87171">OFFLINE</span>'

st.markdown(f"""
<div class="ts-hero">
  <div style="display:flex;align-items:center;gap:16px;">
    <div style="font-size:28px">🌾</div>
    <div>
      <h1 style="margin:0;padding:0;font-weight:800;letter-spacing:-.02em">TerraSynapse V2.0</h1>
      <div style="color:var(--ts-muted)">Plataforma Enterprise de Monitoramento Agrícola</div>
    </div>
    <div style="margin-left:auto;display:flex;gap:.6rem;align-items:center;">
      <span class="ts-badge">{ENV_MODE.upper()} • {BACKEND_URL}</span>
      {online_badge}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
st.write("")

# ----------------------------------------------------------------------
# Sidebar — Portal Executivo (Login/Cadastro + Dev Page)
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

        # Localização — escolha do usuário
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
                with c2: u = st.selectbox("UF", ["MG","SP","GO","MT","MS","PR","RS","SC","BA","TO","MA","PI","CE","RN",
                                                 "PB","PE","AL","SE","ES","RJ","AC","RO","AM","RR","PA","AP","DF"], index=0)
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

        # Página do Desenvolvedor — só para e-mails autorizados
        admin_emails = set(map(str.strip, st.secrets.get("admin", {}).get("EMAILS","").split(","))) if st.secrets.get("admin",{}) else set()
        if st.session_state.user_data and st.session_state.user_data.get("email") in admin_emails:
            with st.expander("🛠️ Página do Desenvolvedor (apenas você vê)"):
                st.write(f"Modo: **{ENV_MODE.upper()}** — Backend: **{BACKEND_URL}**")
                st.code("Endpoints em uso (protegidos): /login, /register, /dashboard/{lat}/{lon}, /market")
                _c, _b = _request("GET", "/health")
                if _c == 200: st.json(_b)

# ----------------------------------------------------------------------
# HOME Enterprise (quando NÃO logado) — Hero + Highlights + Cards + CTA
# ----------------------------------------------------------------------
def home_enterprise():
    st.markdown("### TerraSynapse V2.0 Enterprise")
    st.caption("Plataforma Líder em Inteligência Agrícola")

    # highlights de confiança
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

    # grid de valores
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

    st.markdown("---")

    # CTA
    st.markdown(
        '<div class="cta-wrap">'
        '<a class="btn primary" href="#portal-executivo">🚀 Entrar no Portal</a>'
        '<a class="btn ghost" href="mailto:contato@terrasynapse.com">📩 Falar com Comercial</a>'
        '</div>', unsafe_allow_html=True
    )

# âncora para o botão "Entrar no Portal"
st.markdown('<div id="portal-executivo"></div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Conteúdo principal
# ----------------------------------------------------------------------
if st.session_state.logged_in:
    # Local ativo
    lat = st.session_state.loc["lat"]; lon = st.session_state.loc["lon"]
    cidade = st.session_state.loc.get("cidade",""); uf = st.session_state.loc.get("uf","")
    st.markdown(
        f'<div class="ts-badge"><span class="ts-dot green"></span>'
        f' Local: {cidade}-{uf} • {lat:.4f}, {lon:.4f}</div>',
        unsafe_allow_html=True
    )

    colA, colB = st.columns([1,1])
    with colA:
        if st.button("🔄 Atualizar Dados", type="primary"):
            st.cache_data.clear(); st.rerun()
    with colB:
        auto_refresh = st.checkbox("⚡ Auto-refresh (30s)")
    if auto_refresh:
        time.sleep(30); st.cache_data.clear(); st.rerun()

    st.markdown("---")

    # Dashboard
    code, dash = _request("GET", f"/dashboard/{lat}/{lon}", token=st.session_state.user_token)
    if code == 200 and isinstance(dash, dict) and dash.get("status") == "success":
        data = dash["data"]

        st.subheader("📊 Dashboard Executivo — Tempo Real")
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

        st.markdown("---")
        st.subheader("📈 Análise Técnica Avançada")
        g1, g2 = st.columns(2)

        with g1:
            st.markdown("#### 🌡️ Evapotranspiração (ET0)")
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
            fig.update_layout(height=300, margin=dict(l=20,r=20,t=30,b=10))
            st.plotly_chart(fig, use_container_width=True)

        with g2:
            st.markdown("#### 📈 Preços de Commodities (R$/saca)")
            com = data["mercado"]
            df = pd.DataFrame([
                {"Commodity":"Soja","Preço":com["soja"]["preco"]},
                {"Commodity":"Milho","Preço":com["milho"]["preco"]},
                {"Commodity":"Café","Preço":com["cafe"]["preco"]}
            ])
            figb = px.bar(df, x="Commodity", y="Preço", title=None)
            figb.update_layout(height=300, margin=dict(l=20,r=20,t=10,b=10))
            st.plotly_chart(figb, use_container_width=True)

        st.markdown("---")
        st.subheader("🔬 Análise Técnica Executiva")
        t1, t2, t3 = st.tabs(["🌡️ Climatologia","🌱 Vegetação","💰 Mercado"])

        with t1:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### 📊 Condições Meteorológicas")
                st.write(f"**Temperatura:** {data['clima']['temperatura']}°C")
                st.write(f"**Umidade:** {data['clima']['umidade']}%")
                st.write(f"**Vento:** {data['clima']['vento']} km/h")
                st.write(f"**Pressão:** {data['clima']['pressao']} hPa")
                st.write(f"**Condição:** {data['clima']['descricao']}")
            with c2:
                st.markdown("##### 💧 Gestão de Irrigação")
                st.write(f"**ET0:** {data['clima']['et0']} mm/dia")
                st.write(f"**Recomendação:** {data['clima']['recomendacao_irrigacao']}")
                if data['clima']['et0'] > 6:   st.error("🚨 ET0 elevada - Irrigação urgente recomendada")
                elif data['clima']['et0'] > 4: st.warning("⚠️ ET0 moderada - Monitorar necessidade de irrigação")
                else:                           st.success("✅ ET0 baixa - Irrigação não necessária")

        with t2:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### 🛰️ Análise NDVI")
                st.write(f"**Valor:** {data['vegetacao']['ndvi']}")
                st.write(f"**Status:** {data['vegetacao']['status_vegetacao']}")
                st.write(f"**Data:** {data['vegetacao']['data_analise']}")
            with c2:
                st.markdown("##### 📋 Recomendações Técnicas")
                st.info(data['vegetacao']['recomendacao'])

        with t3:
            st.markdown("##### 📈 Análise de Mercado")
            for commodity, info in data['mercado'].items():
                c1, c2, c3 = st.columns(3)
                with c1: st.metric(f"{commodity.title()}", f"R$ {info['preco']}/saca")
                with c2: st.metric("Variação", f"{info.get('variacao',0):+.2f}%")
                with c3:
                    if commodity == "soja":
                        receita_estimada = info['preco'] * data['rentabilidade']['produtividade_estimada']
                        st.metric("Receita/ha", f"R$ {receita_estimada:,.0f}")

        st.markdown("---")
        st.subheader("🧮 Calculadora Enterprise de Rentabilidade")
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

        st.markdown("---")
        st.caption(f"**TerraSynapse V2.0** — Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | 🟢 Sistema Online")
    else:
        st.error("❌ Não foi possível carregar o dashboard agora. Verifique o login e tente novamente.")
else:
    home_enterprise()
