import streamlit as st
import requests
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="TerraSynapse - Plataforma Agrícola Enterprise",
                   page_icon="🌾", layout="wide", initial_sidebar_state="expanded")

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
BACKEND_URL = st.secrets["api"]["API_BASE_URL"].rstrip("/")

def api_url(path: str) -> str:
    return f"{BACKEND_URL}{path}"

# ----------------------------------------------------------------------
# HTTP helpers
# ----------------------------------------------------------------------
def fazer_requisicao(endpoint, method="GET", data=None, token=None, timeout=15):
    try:
        url = api_url(endpoint)
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=timeout)
        else:
            r = requests.post(url, headers=headers, json=data, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        st.error(f"API {r.status_code}: {r.text[:300]}")
    except requests.exceptions.RequestException as e:
        st.error(f"🔌 Erro de conexão com a API: {e}")
    return None

def obter_localizacao():
    # tenta descobrir por IP (server-side, não bloqueia HTTPS)
    try:
        r = requests.get("https://ipapi.co/json/", timeout=8)
        if r.status_code == 200:
            d = r.json()
            return float(d["latitude"]), float(d["longitude"]), d.get("city",""), d.get("region","")
    except Exception:
        pass
    # fallback: defaults do secrets
    g = st.secrets.get("geo", {})
    return float(g.get("DEFAULT_LAT", -15.78)), float(g.get("DEFAULT_LON", -47.93)), \
           g.get("DEFAULT_CITY","Brasília"), g.get("DEFAULT_STATE","DF")

# ----------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_token" not in st.session_state: st.session_state.user_token = None
if "user_data"  not in st.session_state: st.session_state.user_data  = None

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.title("🌾 TerraSynapse V2.0")
st.subheader("Plataforma Enterprise de Monitoramento Agrícola")
st.caption(f"Backend: {BACKEND_URL}")

st.divider()

# ----------------------------------------------------------------------
# Sidebar (Login/Cadastro + Diagnóstico)
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
                    res = fazer_requisicao("/login", "POST", {"email": email, "password": password})
                    if res and "access_token" in res:
                        st.session_state.logged_in = True
                        st.session_state.user_token = res["access_token"]
                        st.session_state.user_data = res["user"]
                        st.success("✅ Login realizado com sucesso!")
                        time.sleep(0.7)
                        st.rerun()
                    else:
                        st.error("❌ Credenciais inválidas ou API indisponível.")
                else:
                    st.warning("⚠️ Preencha todos os campos")

        with tab2:
            nome = st.text_input("👤 Nome Completo")
            email_reg = st.text_input("📧 Email")
            password_reg = st.text_input("🔒 Senha", type="password")
            perfil = st.selectbox("🎯 Perfil Profissional",
                                  ["Produtor Rural","Agrônomo","Técnico Agrícola","Consultor","Cooperativa","Gerente Agrícola","Outro"])
            empresa = st.text_input("🏢 Empresa")
            cidade  = st.text_input("🌍 Cidade")
            estado  = st.selectbox("📍 Estado", ["SP","MG","MT","GO","MS","PR","RS","SC","BA","TO","MA","PI","CE","RN","PB","PE","AL","SE","ES","RJ","AC","RO","AM","RR","PA","AP","DF"])
            if st.button("🎯 Criar Conta Enterprise", type="primary", use_container_width=True):
                if nome and email_reg and password_reg:
                    payload = {
                        "nome_completo": nome, "email": email_reg, "password": password_reg,
                        "perfil_profissional": perfil, "empresa_propriedade": empresa,
                        "cidade": cidade, "estado": estado
                    }
                    res = fazer_requisicao("/register", "POST", payload)
                    if res and "access_token" in res:
                        st.session_state.logged_in = True
                        st.session_state.user_token = res["access_token"]
                        st.session_state.user_data = res["user"]
                        st.success("✅ Conta criada com sucesso!")
                        time.sleep(0.7)
                        st.rerun()
                    else:
                        st.error("❌ Erro no cadastro")
                else:
                    st.warning("⚠️ Preencha os obrigatórios")
    else:
        st.success(f"👋 Bem-vindo, {st.session_state.user_data['nome']}!")
        st.info("🟢 Sistema Online")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.update({"logged_in": False, "user_token": None, "user_data": None})
            st.rerun()

    st.divider()
    if st.button("🔧 Diagnóstico do Sistema", use_container_width=True):
        health = fazer_requisicao("/health")
        if health: st.success("✅ APIs TerraSynapse Online"); st.json(health)
        else:      st.error("❌ Sistema Temporariamente Indisponível")

# ----------------------------------------------------------------------
# Conteúdo
# ----------------------------------------------------------------------
if st.session_state.logged_in:
    # Localização
    lat, lon, cidade, estado = obter_localizacao()
    st.info(f"📍 Localização: {cidade} - {estado}  •  {lat:.4f}, {lon:.4f}")

    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("🔄 Atualizar Dados", type="primary"): st.rerun()
    with c2:
        auto_refresh = st.checkbox("⚡ Auto-refresh (30s)")
    if auto_refresh:
        time.sleep(30); st.rerun()

    st.divider()

    # Dashboard
    dash = fazer_requisicao(f"/dashboard/{lat}/{lon}", token=st.session_state.user_token)
    if dash and dash.get("status") == "success":
        data = dash["data"]

        st.header("📊 Dashboard Executivo - Tempo Real")
        k1, k2, k3, k4 = st.columns(4)
        with k1: st.metric("🌡️ Temperatura", f"{data['clima']['temperatura']}°C", delta=f"Umidade: {data['clima']['umidade']}%")
        with k2: st.metric("💧 ET0", f"{data['clima']['et0']} mm/dia", delta=("Crítico" if data['clima']['et0'] > 6 else "Normal"))
        with k3: st.metric("🌱 NDVI", f"{data['vegetacao']['ndvi']}", delta=data['vegetacao']['status_vegetacao'])
        with k4:
            rec = data['rentabilidade']['receita_por_hectare']
            st.metric("💰 Receita/ha", f"R$ {rec:,.0f}", delta=f"{data['rentabilidade']['produtividade_estimada']} sc/ha")

        st.divider()

        st.header("⚠️ Centro de Alertas Inteligentes")
        if data["alertas"]:
            for a in data["alertas"]:
                (st.error if a["prioridade"]=="alta" else st.warning)(f"{a['mensagem']}")
        else:
            st.success("✅ SISTEMA OPERACIONAL: Nenhum alerta crítico detectado.")

        st.divider()
        st.header("📈 Análise Técnica Avançada")
        g1, g2 = st.columns(2)

        with g1:
            st.subheader("🌡️ Evapotranspiração (ET0)")
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta", value=data['clima']['et0'],
                title={'text': "ET0 (mm/dia)"}, delta={'reference': 5},
                gauge={'axis': {'range': [None, 10]},
                       'bar': {'color': "#2E7D32"},
                       'steps': [{'range': [0,3], 'color': "lightgray"},
                                 {'range': [3,6], 'color': "yellow"},
                                 {'range': [6,10], 'color': "red"}],
                       'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': .75, 'value': 6}}
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        with g2:
            st.subheader("📈 Preços de Commodities")
            com = data["mercado"]
            df = pd.DataFrame([{"Commodity":"Soja","Preço":com["soja"]["preco"]},
                               {"Commodity":"Milho","Preço":com["milho"]["preco"]},
                               {"Commodity":"Café","Preço":com["cafe"]["preco"]}])
            figb = px.bar(df, x="Commodity", y="Preço", title="Preços Atuais (R$/saca)",
                          color="Preço", color_continuous_scale="Greens")
            figb.update_layout(height=300)
            st.plotly_chart(figb, use_container_width=True)

        st.divider()
        st.header("🔬 Análise Técnica Executiva")
        t1, t2, t3 = st.tabs(["🌡️ Climatologia","🌱 Vegetação","💰 Mercado"])

        with t1:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("📊 Condições Meteorológicas")
                st.write(f"**Temperatura:** {data['clima']['temperatura']}°C")
                st.write(f"**Umidade:** {data['clima']['umidade']}%")
                st.write(f"**Vento:** {data['clima']['vento']} km/h")
                st.write(f"**Pressão:** {data['clima']['pressao']} hPa")
                st.write(f"**Condição:** {data['clima']['descricao']}")
            with c2:
                st.subheader("💧 Gestão de Irrigação")
                st.write(f"**ET0:** {data['clima']['et0']} mm/dia")
                st.write(f"**Recomendação:** {data['clima']['recomendacao_irrigacao']}")
                if data['clima']['et0'] > 6:   st.error("🚨 ET0 elevada - Irrigação urgente recomendada")
                elif data['clima']['et0'] > 4: st.warning("⚠️ ET0 moderada - Monitorar necessidade de irrigação")
                else:                           st.success("✅ ET0 baixa - Irrigação não necessária")

        with t2:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("🛰️ Análise NDVI")
                st.write(f"**Valor:** {data['vegetacao']['ndvi']}")
                st.write(f"**Status:** {data['vegetacao']['status_vegetacao']}")
                st.write(f"**Data:** {data['vegetacao']['data_analise']}")
            with c2:
                st.subheader("📋 Recomendações Técnicas")
                st.info(data['vegetacao']['recomendacao'])

        with t3:
            st.subheader("📈 Análise de Mercado")
            for commodity, info in data['mercado'].items():
                c1, c2, c3 = st.columns(3)
                with c1: st.metric(f"{commodity.title()}", f"R$ {info['preco']}/saca")
                with c2: st.metric("Variação", f"{info['variacao']:+.2f}%")
                with c3:
                    if commodity == "soja":
                        receita_estimada = info['preco'] * data['rentabilidade']['produtividade_estimada']
                        st.metric("Receita/ha", f"R$ {receita_estimada:,.0f}")

        st.divider()
        st.header("🧮 Calculadora Enterprise de Rentabilidade")
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
            st.subheader(f"💰 Projeção Financeira - {cultura}")
            m1,m2,m3 = st.columns(3)
            with m1: st.metric("Receita Total", f"R$ {receita_total:,.0f}")
            with m2: st.metric("Custo Estimado", f"R$ {custo_total:,.0f}")
            with m3: st.metric("Lucro Projetado", f"R$ {lucro_total:,.0f}")
            st.write(f"**Área:** {area} ha | **Produtividade:** {prod} sc/ha | **Preço:** R$ {preco}/saca | **Margem:** {margem:.1f}%")

        st.divider()
        st.write(f"**TerraSynapse V2.0** — Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | 🟢 Sistema Online")
    else:
        st.error("❌ Erro ao carregar dados do dashboard")
else:
    st.header("🌾 TerraSynapse V2.0 Enterprise")
    st.subheader("Plataforma Líder em Inteligência Agrícola")
    st.info("🚀 Faça login ou cadastre-se na barra lateral para acessar dados personalizados da sua propriedade.")
