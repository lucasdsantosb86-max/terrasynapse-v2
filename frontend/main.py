import streamlit as st
import requests
import json
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="TerraSynapse - Sistema Agrícola Inteligente",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #2E7D32 0%, #4CAF50 100%);
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

BACKEND_URL = "https://terrasynapse-backend.onrender.com"

def fazer_requisicao(endpoint, method="GET", data=None, token=None):
    try:
        url = f"{BACKEND_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na API: {response.status_code}")
            return None
    except:
        st.error("Erro de conexão com API")
        return None

def obter_localizacao():
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data["lat"], data["lon"], data["city"], data["region"]
    except:
        pass
    return -15.7942, -47.8822, "Brasília", "DF"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_token" not in st.session_state:
    st.session_state.user_token = None
if "user_data" not in st.session_state:
    st.session_state.user_data = None

st.markdown("""
<div class="main-header">
    <h1>🌾 TerraSynapse V2.0</h1>
    <p>Sistema Inteligente de Monitoramento Agrícola</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🔐 Acesso ao Sistema")
    
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["Login", "Cadastro"])
        
        with tab1:
            st.subheader("Entrar")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Senha", type="password", key="login_password")
            
            if st.button("Entrar", type="primary"):
                if email and password:
                    with st.spinner("Autenticando..."):
                        result = fazer_requisicao("/login", "POST", {
                            "email": email,
                            "password": password
                        })
                        
                        if result and "access_token" in result:
                            st.session_state.logged_in = True
                            st.session_state.user_token = result["access_token"]
                            st.session_state.user_data = result["user"]
                            st.success("Login realizado com sucesso!")
                            st.rerun()
                        else:
                            st.error("Email ou senha incorretos")
                else:
                    st.warning("Preencha todos os campos")
        
        with tab2:
            st.subheader("Cadastrar")
            nome = st.text_input("Nome Completo", key="reg_nome")
            email_reg = st.text_input("Email", key="reg_email")
            password_reg = st.text_input("Senha", type="password", key="reg_password")
            
            if st.button("Cadastrar", type="primary"):
                if nome and email_reg and password_reg:
                    with st.spinner("Criando conta..."):
                        result = fazer_requisicao("/register", "POST", {
                            "nome_completo": nome,
                            "email": email_reg,
                            "password": password_reg
                        })
                        
                        if result and "access_token" in result:
                            st.session_state.logged_in = True
                            st.session_state.user_token = result["access_token"]
                            st.session_state.user_data = result["user"]
                            st.success("Conta criada com sucesso!")
                            st.rerun()
                        else:
                            st.error("Erro no cadastro")
                else:
                    st.warning("Preencha todos os campos obrigatórios")
    
    else:
        st.success(f"Olá, {st.session_state.user_data['nome']}")
        if st.button("Sair"):
            st.session_state.logged_in = False
            st.session_state.user_token = None
            st.session_state.user_data = None
            st.rerun()

if st.session_state.logged_in:
    lat, lon, cidade, estado = obter_localizacao()
    
    st.info(f"Localização: {cidade}, {estado} ({lat:.4f}, {lon:.4f})")
    
    if st.button("🔄 Atualizar Dados", type="primary"):
        st.rerun()
    
    with st.spinner("Carregando dados..."):
        dashboard_data = fazer_requisicao(
            f"/dashboard/{lat}/{lon}", 
            token=st.session_state.user_token
        )
    
    if dashboard_data and dashboard_data.get("status") == "success":
        data = dashboard_data["data"]
        
        st.subheader("📊 Monitoramento em Tempo Real")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌡️ Temperatura", f"{data['clima']['temperatura']}°C")
        
        with col2:
            st.metric("💧 ET0", f"{data['clima']['et0']} mm/dia")
        
        with col3:
            st.metric("🌱 NDVI", f"{data['vegetacao']['ndvi']}")
        
        with col4:
            st.metric("💰 Receita/ha", f"R$ {data['rentabilidade']['receita_por_hectare']:,.2f}")
        
        if data["alertas"]:
            st.subheader("⚠️ Alertas Importantes")
            for alerta in data["alertas"]:
                if alerta["prioridade"] == "alta":
                    st.error(f"🚨 {alerta['mensagem']}")
                else:
                    st.warning(f"⚠️ {alerta['mensagem']}")
        else:
            st.success("✅ Nenhum alerta crítico no momento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌡️ Condições Climáticas")
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = data['clima']['et0'],
                title = {'text': "ET0 (mm/dia)"},
                gauge = {
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 3], 'color': "lightgray"},
                        {'range': [3, 6], 'color': "yellow"},
                        {'range': [6, 10], 'color': "red"}
                    ]
                }
            ))
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            st.subheader("📈 Preços de Commodities")
            commodities = data["mercado"]
            df_precos = pd.DataFrame([
                {"Commodity": "Soja", "Preço": commodities["soja"]["preco"]},
                {"Commodity": "Milho", "Preço": commodities["milho"]["preco"]},
                {"Commodity": "Café", "Preço": commodities["cafe"]["preco"]}
            ])
            
            fig_bar = px.bar(df_precos, x="Commodity", y="Preço", title="Preços Atuais (R$/saca)")
            st.plotly_chart(fig_bar, use_container_width=True)
    
    else:
        st.error("Erro ao carregar dados do dashboard")

else:
    st.markdown("""
    ## 🌾 Bem-vindo ao TerraSynapse V2.0
    
    ### Sistema Inteligente de Monitoramento Agrícola
    
    **Funcionalidades principais:**
    - 🌡️ Monitoramento climático em tempo real
    - 🛰️ Análise NDVI por satélite  
    - 💰 Preços de commodities atualizados
    - 📊 Dashboard integrado com alertas
    
    **Para começar:**
    1. Faça login ou cadastre-se na barra lateral
    2. O sistema detectará automaticamente sua localização
    3. Explore os dados em tempo real da sua região
    """)
