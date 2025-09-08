import streamlit as st
import requests
import json
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="TerraSynapse - Plataforma Agtech Enterprise",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Enterprise Profissional
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Reset e Base */
.main > div {
    padding-top: 0rem !important;
}

.stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* Header Enterprise */
.enterprise-header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    padding: 2rem;
    border-radius: 16px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(30, 60, 114, 0.3);
    position: relative;
    overflow: hidden;
}

.enterprise-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
    opacity: 0.1;
}

.enterprise-header h1 {
    font-size: 3rem;
    font-weight: 700;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    position: relative;
    z-index: 1;
}

.enterprise-header p {
    font-size: 1.2rem;
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    position: relative;
    z-index: 1;
}

/* Logo Integration */
.logo-section {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.logo-icon {
    width: 48px;
    height: 48px;
    background: #2E7D32;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    font-weight: bold;
}

/* Sidebar Enterprise */
.css-1d391kg {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
}

.sidebar-content {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* Cards Enterprise */
.metric-card-enterprise {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.metric-card-enterprise:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
}

.metric-card-enterprise::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(45deg, #2E7D32, #4CAF50);
}

/* Alertas Profissionais */
.alert-enterprise {
    background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    border: none;
    border-left: 4px solid #ff9800;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin: 0.5rem 0;
    box-shadow: 0 4px 16px rgba(255, 152, 0, 0.2);
}

.alert-success-enterprise {
    background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
    border-left-color: #4caf50;
    box-shadow: 0 4px 16px rgba(76, 175, 80, 0.2);
}

.alert-error-enterprise {
    background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
    border-left-color: #f44336;
    box-shadow: 0 4px 16px rgba(244, 67, 54, 0.2);
}

/* Dashboards Executivos */
.dashboard-section {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 16px 64px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e3c72;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e3f2fd;
}

/* Botões Enterprise */
.stButton > button {
    background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
    border: none;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    font-size: 1rem;
    color: white;
    box-shadow: 0 4px 16px rgba(46, 125, 50, 0.3);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(46, 125, 50, 0.4);
}

/* Inputs Profissionais */
.stTextInput > div > div > input {
    border-radius: 12px;
    border: 2px solid #e0e0e0;
    padding: 1rem;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus {
    border-color: #2E7D32;
    box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.1);
}

/* Métricas Executivas */
.metric-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1e3c72;
    margin: 0.5rem 0;
}

.metric-label {
    font-size: 0.9rem;
    color: #666;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-delta {
    font-size: 0.8rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-weight: 600;
    margin-top: 0.5rem;
}

/* Status Indicators */
.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
}

.status-online {
    background: rgba(76, 175, 80, 0.1);
    color: #2e7d32;
    border: 1px solid rgba(76, 175, 80, 0.3);
}

.status-warning {
    background: rgba(255, 152, 0, 0.1);
    color: #f57c00;
    border: 1px solid rgba(255, 152, 0, 0.3);
}

.status-error {
    background: rgba(244, 67, 54, 0.1);
    color: #c62828;
    border: 1px solid rgba(244, 67, 54, 0.3);
}

/* Gráficos Profissionais */
.chart-container {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
    margin: 1rem 0;
}

/* Footer Enterprise */
.footer-enterprise {
    text-align: center;
    padding: 2rem;
    color: #666;
    font-size: 0.9rem;
    border-top: 1px solid #e0e0e0;
    margin-top: 3rem;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
}

/* Responsivo */
@media (max-width: 768px) {
    .enterprise-header h1 {
        font-size: 2rem;
    }
    
    .enterprise-header p {
        font-size: 1rem;
    }
    
    .metric-value {
        font-size: 2rem;
    }
}

/* Animações */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in-up {
    animation: fadeInUp 0.6s ease-out;
}

/* Loading Spinners Enterprise */
.loading-enterprise {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 3rem;
}

.spinner-enterprise {
    width: 40px;
    height: 40px;
    border: 4px solid #e3f2fd;
    border-top: 4px solid #2E7D32;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
""", unsafe_allow_html=True)

# URLs das APIs
BACKEND_URL = "https://terrasynapse-backend.onrender.com"

def fazer_requisicao(endpoint, method="GET", data=None, token=None):
    """Função para fazer requisições à API"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=15)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"⚠️ Erro na API: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        st.warning("⏱️ Tempo limite excedido - API inicializando (aguarde 30s)")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"🔌 Erro de conexão: {str(e)}")
        return None

def obter_localizacao():
    """Obter localização via IP"""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=8)
        if response.status_code == 200:
            data = response.json()
            return data["lat"], data["lon"], data["city"], data["region"]
    except:
        pass
    
    # Coordenadas padrão (Brasília)
    return -15.7942, -47.8822, "Brasília", "DF"

# Inicialização do estado da sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_token" not in st.session_state:
    st.session_state.user_token = None
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# Header Enterprise com Logo
st.markdown("""
<div class="enterprise-header fade-in-up">
    <div class="logo-section">
        <div class="logo-icon">🌾</div>
        <div>
            <h1>TerraSynapse</h1>
            <p>Plataforma Enterprise de Monitoramento Agrícola</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar Enterprise
with st.sidebar:
    st.markdown("""
    <div class="sidebar-content">
        <h2 style="color: #1e3c72; margin-bottom: 1.5rem; font-weight: 600;">🔐 Portal Executivo</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["🔑 Login", "👤 Cadastro"])
        
        with tab1:
            st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
            st.subheader("Acesso Executivo")
            
            email = st.text_input("📧 Email Corporativo", key="login_email", placeholder="seu.email@empresa.com")
            password = st.text_input("🔒 Senha", type="password", key="login_password", placeholder="Senha segura")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🚀 Entrar", type="primary", use_container_width=True):
                    if email and password:
                        with st.spinner("🔄 Autenticando..."):
                            result = fazer_requisicao("/login", "POST", {
                                "email": email,
                                "password": password
                            })
                            
                            if result and "access_token" in result:
                                st.session_state.logged_in = True
                                st.session_state.user_token = result["access_token"]
                                st.session_state.user_data = result["user"]
                                st.success("✅ Login realizado com sucesso!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Credenciais inválidas")
                    else:
                        st.warning("⚠️ Preencha todos os campos")
            
            with col2:
                if st.button("🔄 Limpar", use_container_width=True):
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
            st.subheader("Registro Enterprise")
            
            nome = st.text_input("👤 Nome Completo", key="reg_nome", placeholder="João Silva")
            email_reg = st.text_input("📧 Email", key="reg_email", placeholder="joao@fazenda.com")
            password_reg = st.text_input("🔒 Senha", type="password", key="reg_password", placeholder="Mínimo 8 caracteres")
            
            perfil = st.selectbox("🎯 Perfil Profissional", [
                "Produtor Rural", "Agrônomo", "Técnico Agrícola", 
                "Consultor", "Cooperativa", "Gerente Agrícola", "Outro"
            ])
            
            col1, col2 = st.columns(2)
            with col1:
                empresa = st.text_input("🏢 Empresa", key="reg_empresa", placeholder="Fazenda São João")
            with col2:
                cidade = st.text_input("🌍 Cidade", key="reg_cidade", placeholder="Ribeirão Preto")
            
            estado = st.selectbox("📍 Estado", [
                "SP", "MG", "MT", "GO", "MS", "PR", "RS", "SC",
                "BA", "TO", "MA", "PI", "CE", "RN", "PB", "PE",
                "AL", "SE", "ES", "RJ", "AC", "RO", "AM", "RR", 
                "PA", "AP", "DF"
            ])
            
            if st.button("🎯 Criar Conta Enterprise", type="primary", use_container_width=True):
                if nome and email_reg and password_reg:
                    with st.spinner("🔄 Criando conta..."):
                        result = fazer_requisicao("/register", "POST", {
                            "nome_completo": nome,
                            "email": email_reg,
                            "password": password_reg,
                            "perfil_profissional": perfil,
                            "empresa_propriedade": empresa,
                            "cidade": cidade,
                            "estado": estado
                        })
                        
                        if result and "access_token" in result:
                            st.session_state.logged_in = True
                            st.session_state.user_token = result["access_token"]
                            st.session_state.user_data = result["user"]
                            st.success("✅ Conta criada com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Erro no cadastro - Tente novamente")
                else:
                    st.warning("⚠️ Preencha todos os campos obrigatórios")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        st.markdown(f"""
        <div class="sidebar-content">
            <div style="text-align: center; padding: 1rem;">
                <div style="background: linear-gradient(135deg, #2E7D32, #4CAF50); color: white; padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
                    <h3 style="margin: 0;">👋 Bem-vindo!</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{st.session_state.user_data['nome']}</p>
                </div>
                <div class="status-indicator status-online">
                    <span>🟢</span> Sistema Online
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_token = None
            st.session_state.user_data = None
            st.rerun()

# Conteúdo principal
if st.session_state.logged_in:
    # Obter localização
    lat, lon, cidade, estado = obter_localizacao()
    
    st.markdown(f"""
    <div class="dashboard-section fade-in-up">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h3 style="margin: 0; color: #1e3c72;">📍 Localização Detectada</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">{cidade}, {estado} • {lat:.4f}, {lon:.4f}</p>
            </div>
            <div style="display: flex; gap: 1rem;">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 Atualizar Dados", type="primary"):
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("⚡ Auto-refresh (30s)")
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Buscar dados do dashboard
    with st.spinner("🔄 Carregando inteligência agrícola..."):
        dashboard_data = fazer_requisicao(
            f"/dashboard/{lat}/{lon}", 
            token=st.session_state.user_token
        )
    
    if dashboard_data and dashboard_data.get("status") == "success":
        data = dashboard_data["data"]
        
        # Métricas principais
        st.markdown("""
        <div class="dashboard-section fade-in-up">
            <h2 class="section-title">📊 Dashboard Executivo - Tempo Real</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card-enterprise">
                <div class="metric-container">
                    <div style="color: #ff5722; font-size: 2rem;">🌡️</div>
                    <div class="metric-value">{data["clima"]["temperatura"]}°C</div>
                    <div class="metric-label">Temperatura</div>
                    <div class="metric-delta" style="background: rgba(33, 150, 243, 0.1); color: #1976d2;">
                        Umidade: {data['clima']['umidade']}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            et0_color = "#f44336" if data["clima"]["et0"] > 6 else "#ff9800" if data["clima"]["et0"] > 4 else "#4caf50"
            st.markdown(f"""
            <div class="metric-card-enterprise">
                <div class="metric-container">
                    <div style="color: #2196f3; font-size: 2rem;">💧</div>
                    <div class="metric-value" style="color: {et0_color};">{data["clima"]["et0"]}</div>
                    <div class="metric-label">ET0 (mm/dia)</div>
                    <div class="metric-delta" style="background: rgba({et0_color[1:]}, 0.1); color: {et0_color};">
                        {data['clima']['recomendacao_irrigacao']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            ndvi_color = data['vegetacao']['cor']
            st.markdown(f"""
            <div class="metric-card-enterprise">
                <div class="metric-container">
                    <div style="color: #4caf50; font-size: 2rem;">🌱</div>
                    <div class="metric-value" style="color: {ndvi_color};">{data["vegetacao"]["ndvi"]}</div>
                    <div class="metric-label">NDVI Índice</div>
                    <div class="metric-delta" style="background: {ndvi_color}20; color: {ndvi_color};">
                        {data['vegetacao']['status_vegetacao']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            receita = data["rentabilidade"]["receita_por_hectare"]
            st.markdown(f"""
            <div class="metric-card-enterprise">
                <div class="metric-container">
                    <div style="color: #ff9800; font-size: 2rem;">💰</div>
                    <div class="metric-value" style="color: #2e7d32;">R$ {receita:,.0f}</div>
                    <div class="metric-label">Receita/Hectare</div>
                    <div class="metric-delta" style="background: rgba(46, 125, 50, 0.1); color: #2e7d32;">
                        {data['rentabilidade']['produtividade_estimada']} sc/ha
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Sistema de Alertas Enterprise
        st.markdown("""
        <div class="dashboard-section fade-in-up">
            <h2 class="section-title">⚠️ Centro de Alertas Inteligentes</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if data["alertas"]:
            for alerta in data["alertas"]:
                if alerta["prioridade"] == "alta":
                    st.markdown(f"""
                    <div class="alert-enterprise alert-error-enterprise">
                        <strong>🚨 ALERTA CRÍTICO:</strong> {alerta['mensagem']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="alert-enterprise">
                        <strong>⚠️ ATENÇÃO:</strong> {alerta['mensagem']}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-enterprise alert-success-enterprise">
                <strong>✅ SISTEMA OPERACIONAL:</strong> Nenhum alerta crítico detectado. Propriedade em condições ideais.
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos Executivos
        st.markdown("""
        <div class="dashboard-section fade-in-up">
            <h2 class="section-title">📈 Análise Técnica Avançada</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            
            # Gráfico de gauge ET0 profissional
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = data['clima']['et0'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Evapotranspiração (ET0)", 'font': {'size': 20, 'color': '#1e3c72'}},
                delta = {'reference': 5},
                gauge = {
                    'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "#1e3c72"},
                    'bar': {'color': "#2E7D32", 'thickness': 0.3},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e0e0e0",
                    'steps': [
                        {'range': [0, 3], 'color': "#e8f5e8"},
                        {'range': [3, 6], 'color': "#fff3e0"},
                        {'range': [6, 10], 'color': "#ffebee"}
                    ],
                    'threshold': {
                        'line': {'color': "#f44336", 'width': 4},
                        'thickness': 0.75,
                        'value': 6
                    }
                }
            ))
            
            fig_gauge.update_layout(
                height=350,
                font={'color': "#1e3c72", 'family': "Inter"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            
            # Gráfico de commodities profissional
            commodities = data["mercado"]
            df_precos = pd.DataFrame([
                {
                    "Commodity": "Soja", 
                    "Preço": commodities["soja"]["preco"], 
                    "Variação": commodities["soja"]["variacao"],
                    "Tendência": commodities["soja"]["tendencia"]
                },
                {
                    "Commodity": "Milho", 
                    "Preço": commodities["milho"]["preco"], 
                    "Variação": commodities["milho"]["variacao"],
                    "Tendência": commodities["milho"]["tendencia"]
                },
                {
                    "Commodity": "Café", 
                    "Preço": commodities["cafe"]["preco"], 
                    "Variação": commodities["cafe"]["variacao"],
                    "Tendência": commodities["cafe"]["tendencia"]
                }
            ])
            
            # Cores baseadas na variação
            colors = ['#4CAF50' if x >= 0 else '#F44336' for x in df_precos['Variação']]
            
            fig_bar = px.bar(
                df_precos, 
                x="Commodity", 
                y="Preço",
                color="Variação",
                color_continuous_scale="RdYlGn",
                title="Commodities - Preços Atuais (R$/saca)",
                text=[f"R$ {p:.0f}" for p in df_precos["Preço"]]
            )
            
            fig_bar.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                marker_line_color='rgb(8,48,107)',
                marker_line_width=1.5,
                opacity=0.8
            )
            
            fig_bar.update_layout(
                height=350,
                font={'color': "#1e3c72", 'family': "Inter"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                title_font_size=16,
                title_font_color="#1e3c72",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Análise Detalhada Enterprise
        st.markdown("""
        <div class="dashboard-section fade-in-up">
            <h2 class="section-title">🔬 Análise Técnica Executiva</h2>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Climatologia", "🌱 Vegetação", "💰 Mercado", "📊 Rentabilidade"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="metric-card-enterprise">
                    <h4 style="color: #1e3c72; margin-bottom: 1rem;">📊 Condições Meteorológicas</h4>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                    <div><strong>Temperatura:</strong> {data['clima']['temperatura']}°C</div>
                    <div><strong>Umidade:</strong> {data['clima']['umidade']}%</div>
                    <div><strong>Vento:</strong> {data['clima']['vento']} km/h</div>
                    <div><strong>Pressão:</strong> {data['clima']['pressao']} hPa</div>
                </div>
                <div style="margin-top: 1rem; padding: 1rem; background: #f5f5f5; border-radius: 8px;">
                    <strong>Condição:</strong> {data['clima']['descricao']}
                </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card-enterprise">
                    <h4 style="color: #1e3c72; margin-bottom: 1rem;">💧 Gestão de Irrigação</h4>
                """, unsafe_allow_html=True)
                
                et0_status = "CRÍTICO" if data['clima']['et0'] > 6 else "MODERADO" if data['clima']['et0'] > 4 else "NORMAL"
                et0_color = "#f44336" if data['clima']['et0'] > 6 else "#ff9800" if data['clima']['et0'] > 4 else "#4caf50"
                
                st.markdown(f"""
                <div style="margin: 1rem 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span><strong>ET0:</strong> {data['clima']['et0']} mm/dia</span>
                        <span style="color: {et0_color}; font-weight: bold;">{et0_status}</span>
                    </div>
                    <div style="background: #e0e0e0; height: 8px; border-radius: 4px;">
                        <div style="background: {et0_color}; height: 8px; width: {min(data['clima']['et0']/10*100, 100)}%; border-radius: 4px;"></div>
                    </div>
                </div>
                <div style="margin-top: 1rem; padding: 1rem; background: {et0_color}20; border-left: 4px solid {et0_color}; border-radius: 4px;">
                    <strong>Recomendação:</strong> {data['clima']['recomendacao_irrigacao']}
                </div>
                </div>
                """, unsafe_allow_html=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="metric-card-enterprise">
                    <h4 style="color: #1e3c72; margin-bottom: 1rem;">🛰️ Análise NDVI</h4>
                """, unsafe_allow_html=True)
                
                ndvi_color = data['vegetacao']['cor']
                ndvi_percent = data['vegetacao']['ndvi'] * 100
                
                st.markdown(f"""
                <div style="text-align: center; margin: 1.5rem 0;">
                    <div style="background: {ndvi_color}; color: white; padding: 2rem; border-radius: 50%; width: 120px; height: 120px; margin: 0 auto; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 8px 24px {ndvi_color}40;">
                        <div style="font-size: 1.5rem; font-weight: bold;">{data['vegetacao']['ndvi']}</div>
                        <div style="font-size: 0.9rem; opacity: 0.9;">NDVI</div>
                    </div>
                    <h3 style="margin: 1rem 0; color: {ndvi_color};">{data['vegetacao']['status_vegetacao']}</h3>
                </div>
                <div style="margin-top: 1rem;">
                    <strong>Data da Análise:</strong> {data['vegetacao']['data_analise']}
                </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card-enterprise">
                    <h4 style="color: #1e3c72; margin-bottom: 1rem;">📋 Recomendações Técnicas</h4>
                """, unsafe_allow_html=True)
                
                ndvi_val = data['vegetacao']['ndvi']
                if ndvi_val > 0.7:
                    status_icon = "🌟"
                    status_text = "Vegetação saudável e vigorosa"
                    status_color = "#4caf50"
                elif ndvi_val > 0.5:
                    status_icon = "📈"
                    status_text = "Vegetação em desenvolvimento normal"
                    status_color = "#8bc34a"
                elif ndvi_val > 0.3:
                    status_icon = "📉"
                    status_text = "Vegetação com estresse moderado"
                    status_color = "#ff9800"
                else:
                    status_icon = "🚨"
                    status_text = "Vegetação em estado crítico"
                    status_color = "#f44336"
                
                st.markdown(f"""
                <div style="margin: 1rem 0; padding: 1.5rem; background: {status_color}20; border-left: 4px solid {status_color}; border-radius: 8px;">
                    <div style="font-size: 1.2rem; margin-bottom: 1rem;">
                        {status_icon} <strong>{status_text}</strong>
                    </div>
                    <div style="color: #666; line-height: 1.6;">
                        {data['vegetacao']['recomendacao']}
                    </div>
                </div>
                </div>
                """, unsafe_allow_html=True)
        
        with tab3:
            st.markdown("""
            <div class="metric-card-enterprise">
                <h4 style="color: #1e3c72; margin-bottom: 1.5rem;">📈 Análise de Mercado Executiva</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for commodity, info in data['mercado'].items():
                col1, col2, col3, col4 = st.columns(4)
                
                trend_color = "#4caf50" if info['variacao'] > 0 else "#f44336" if info['variacao'] < 0 else "#ff9800"
                trend_icon = "📈" if info['variacao'] > 0 else "📉" if info['variacao'] < 0 else "➡️"
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card-enterprise" style="text-align: center;">
                        <h5 style="color: #1e3c72; margin-bottom: 0.5rem;">{commodity.title()}</h5>
                        <div style="font-size: 1.8rem; font-weight: bold; color: #2e7d32;">R$ {info['preco']}</div>
                        <div style="font-size: 0.9rem; color: #666;">por saca</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card-enterprise" style="text-align: center;">
                        <div style="color: {trend_color}; font-size: 1.5rem; margin-bottom: 0.5rem;">{trend_icon}</div>
                        <div style="font-size: 1.2rem; font-weight: bold; color: {trend_color};">{info['variacao']:+.2f}%</div>
                        <div style="font-size: 0.9rem; color: #666;">variação</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card-enterprise" style="text-align: center;">
                        <div style="font-size: 1rem; margin-bottom: 0.5rem; font-weight: bold; color: {trend_color};">{info['tendencia']}</div>
                        <div style="font-size: 0.9rem; color: #666;">tendência</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    if commodity == "soja":
                        receita_estimada = info['preco'] * data['rentabilidade']['produtividade_estimada']
                        st.markdown(f"""
                        <div class="metric-card-enterprise" style="text-align: center;">
                            <div style="font-size: 1.2rem; font-weight: bold; color: #2e7d32;">R$ {receita_estimada:,.0f}</div>
                            <div style="font-size: 0.9rem; color: #666;">receita/ha</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        with tab4:
            st.markdown("""
            <div class="metric-card-enterprise">
                <h4 style="color: #1e3c72; margin-bottom: 1.5rem;">🧮 Calculadora Enterprise de Rentabilidade</h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                area_ha = st.number_input("🌾 Área (hectares)", min_value=1, value=10, step=1)
            
            with col2:
                cultura_select = st.selectbox("🌱 Cultura Principal", ["Soja", "Milho", "Café"])
            
            with col3:
                produtividade = st.number_input("📊 Produtividade (sacas/ha)", min_value=1, value=50, step=1)
            
            if cultura_select.lower() in data['mercado']:
                preco_cultura = data['mercado'][cultura_select.lower()]['preco']
                receita_total = area_ha * produtividade * preco_cultura
                receita_por_ha = receita_total / area_ha
                
                # Custos estimados (simplificado)
                custo_por_ha = 3000  # Estimativa média
                custo_total = area_ha * custo_por_ha
                lucro_total = receita_total - custo_total
                margem = (lucro_total / receita_total) * 100 if receita_total > 0 else 0
                
                st.markdown(f"""
                <div class="metric-card-enterprise">
                    <h4 style="color: #1e3c72; margin-bottom: 1rem;">💰 Projeção Financeira - {cultura_select}</h4>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin: 1.5rem 0;">
                        <div style="text-align: center; padding: 1rem; background: #e8f5e8; border-radius: 8px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #2e7d32;">R$ {receita_total:,.0f}</div>
                            <div style="color: #666; font-size: 0.9rem;">Receita Total</div>
                        </div>
                        <div style="text-align: center; padding: 1rem; background: #fff3e0; border-radius: 8px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #f57c00;">R$ {custo_total:,.0f}</div>
                            <div style="color: #666; font-size: 0.9rem;">Custo Estimado</div>
                        </div>
                        <div style="text-align: center; padding: 1rem; background: #e3f2fd; border-radius: 8px;">
                            <div style="font-size: 1.5rem; font-weight: bold; color: #1976d2;">R$ {lucro_total:,.0f}</div>
                            <div style="color: #666; font-size: 0.9rem;">Lucro Projetado</div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 1.5rem; padding: 1rem; background: #f5f5f5; border-radius: 8px;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem; text-align: center;">
                            <div><strong>Área:</strong> {area_ha} ha</div>
                            <div><strong>Produtividade:</strong> {produtividade} sc/ha</div>
                            <div><strong>Preço:</strong> R$ {preco_cultura}/saca</div>
                            <div><strong>Margem:</strong> {margem:.1f}%</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if receita_total > 200000:
                    st.success("🎯 Excelente potencial de receita! Propriedade altamente rentável.")
                elif receita_total > 100000:
                    st.info("📊 Boa projeção de receita. Considere otimizações para maximizar lucros.")
                else:
                    st.warning("💡 Receita moderada. Analise possibilidades de aumento de produtividade ou área.")
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer Enterprise
        st.markdown(f"""
        <div class="footer-enterprise fade-in-up">
            <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
                <div>
                    <strong>TerraSynapse V2.0</strong> - Plataforma Enterprise de Monitoramento Agrícola
                </div>
                <div>
                    Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                </div>
                <div>
                    <span class="status-indicator status-online">
                        <span>🟢</span> Sistema Online
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div class="dashboard-section">
            <div class="loading-enterprise">
                <div class="spinner-enterprise"></div>
            </div>
            <div style="text-align: center; color: #666;">
                <h3>🔄 Conectando com APIs Enterprise...</h3>
                <p>Aguarde enquanto sincronizamos os dados em tempo real</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Teste de conectividade
        health_check = fazer_requisicao("/health")
        if health_check:
            st.success("✅ Backend Online - Dados sendo carregados...")
        else:
            st.error("❌ Backend Temporariamente Indisponível - Aguarde...")

else:
    # Página de demonstração enterprise
    st.markdown("""
    <div class="dashboard-section fade-in-up">
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: #1e3c72; margin-bottom: 2rem;">🌾 TerraSynapse V2.0 Enterprise</h2>
            <h3 style="color: #666; font-weight: 400; margin-bottom: 3rem;">Plataforma Líder em Inteligência Agrícola</h3>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 3rem 0;">
            <div class="metric-card-enterprise">
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🌡️</div>
                    <h4 style="color: #1e3c72;">Monitoramento Climático</h4>
                    <p style="color: #666; line-height: 1.6;">Dados meteorológicos em tempo real com cálculo preciso de evapotranspiração e recomendações inteligentes de irrigação.</p>
                </div>
            </div>
            
            <div class="metric-card-enterprise">
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🛰️</div>
                    <h4 style="color: #1e3c72;">Análise por Satélite</h4>
                    <p style="color: #666; line-height: 1.6;">Índices NDVI avançados para monitoramento da saúde vegetal com alertas automáticos de estresse.</p>
                </div>
            </div>
            
            <div class="metric-card-enterprise">
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">💰</div>
                    <h4 style="color: #1e3c72;">Inteligência de Mercado</h4>
                    <p style="color: #666; line-height: 1.6;">Preços atualizados de commodities com análise de tendências e calculadora de rentabilidade.</p>
                </div>
            </div>
            
            <div class="metric-card-enterprise">
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                    <h4 style="color: #1e3c72;">Dashboard Executivo</h4>
                    <p style="color: #666; line-height: 1.6;">Visão completa da propriedade com alertas inteligentes e relatórios automatizados.</p>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 3rem 0;">
            <h3 style="color: #1e3c72;">🚀 Pronto para Revolucionar sua Agricultura?</h3>
            <p style="color: #666; font-size: 1.1rem; margin: 1rem 0;">Faça login ou cadastre-se na barra lateral para acessar dados personalizados da sua propriedade.</p>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem; margin: 2rem 0;">
            <div style="text-align: center; padding: 1rem;">
                <div class="metric-value" style="color: #4caf50;">24.5°C</div>
                <div class="metric-label">Temperatura Ideal</div>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div class="metric-value" style="color: #2e7d32;">0.75</div>
                <div class="metric-label">NDVI Saudável</div>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div class="metric-value" style="color: #1976d2;">R$ 165.50</div>
                <div class="metric-label">Soja (+2.3%)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# API Status Check
if st.sidebar.button("🔧 Diagnóstico do Sistema", use_container_width=True):
    with st.spinner("🔄 Executando diagnóstico..."):
        health = fazer_requisicao("/health")
        if health:
            st.sidebar.success("✅ APIs Enterprise Online")
            st.sidebar.json(health)
        else:
            st.sidebar.error("❌ Sistema Temporariamente Indisponível")
