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
    page_title="TerraSynapse - Plataforma Agrícola Enterprise",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS TerraSynapse Branded
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Reset e Base - TerraSynapse Colors */
.main > div {
    padding-top: 0rem !important;
}

.stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(135deg, #f8fffe 0%, #e8f5f0 100%);
}

/* Header TerraSynapse Branded */
.terrasynapse-header {
    background: linear-gradient(135deg, #2c5530 0%, #4a7c59 100%);
    padding: 2rem;
    border-radius: 16px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(44, 85, 48, 0.3);
    position: relative;
    overflow: hidden;
}

.terrasynapse-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
    opacity: 0.1;
}

.terrasynapse-header h1 {
    font-size: 3rem;
    font-weight: 700;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    position: relative;
    z-index: 1;
}

.terrasynapse-header p {
    font-size: 1.2rem;
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    position: relative;
    z-index: 1;
}

/* Logo TerraSynapse */
.logo-terrasynapse {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.logo-icon-terrasynapse {
    width: 60px;
    height: 60px;
    background: #4a7c59;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    font-weight: bold;
    border: 3px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

/* Sidebar TerraSynapse */
.sidebar-terrasynapse {
    background: linear-gradient(180deg, #2c5530 0%, #1a3a1e 100%);
}

.sidebar-content-terrasynapse {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(44, 85, 48, 0.15);
    border: 1px solid rgba(74, 124, 89, 0.2);
}

/* Cards TerraSynapse */
.metric-card-terrasynapse {
    background: linear-gradient(135deg, #ffffff 0%, #f8fffe 100%);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(44, 85, 48, 0.1);
    border: 1px solid rgba(74, 124, 89, 0.1);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.metric-card-terrasynapse:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 48px rgba(44, 85, 48, 0.2);
}

.metric-card-terrasynapse::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(45deg, #2c5530, #4a7c59);
}

/* Alertas TerraSynapse */
.alert-terrasynapse {
    background: linear-gradient(135deg, #fff9e6 0%, #fef3d4 100%);
    border: none;
    border-left: 4px solid #ff9800;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin: 0.5rem 0;
    box-shadow: 0 4px 16px rgba(255, 152, 0, 0.15);
}

.alert-success-terrasynapse {
    background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%);
    border-left-color: #4a7c59;
    box-shadow: 0 4px 16px rgba(74, 124, 89, 0.15);
}

.alert-error-terrasynapse {
    background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
    border-left-color: #f44336;
    box-shadow: 0 4px 16px rgba(244, 67, 54, 0.15);
}

/* Dashboard TerraSynapse */
.dashboard-section-terrasynapse {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 16px 64px rgba(44, 85, 48, 0.1);
    border: 1px solid rgba(74, 124, 89, 0.1);
}

.section-title-terrasynapse {
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c5530;
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e8f5e8;
}

/* Botões TerraSynapse */
.stButton > button {
    background: linear-gradient(135deg, #2c5530 0%, #4a7c59 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    color: white !important;
    box-shadow: 0 4px 16px rgba(44, 85, 48, 0.3) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(44, 85, 48, 0.4) !important;
}

/* Inputs TerraSynapse */
.stTextInput > div > div > input {
    border-radius: 12px !important;
    border: 2px solid #e0e0e0 !important;
    padding: 1rem !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: #4a7c59 !important;
    box-shadow: 0 0 0 3px rgba(74, 124, 89, 0.1) !important;
}

/* Métricas TerraSynapse */
.metric-container-terrasynapse {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 1rem;
}

.metric-value-terrasynapse {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2c5530;
    margin: 0.5rem 0;
}

.metric-label-terrasynapse {
    font-size: 0.9rem;
    color: #666;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-delta-terrasynapse {
    font-size: 0.8rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-weight: 600;
    margin-top: 0.5rem;
    background: rgba(74, 124, 89, 0.1);
    color: #2c5530;
}

/* Status Indicators TerraSynapse */
.status-indicator-terrasynapse {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
}

.status-online-terrasynapse {
    background: rgba(74, 124, 89, 0.1);
    color: #2c5530;
    border: 1px solid rgba(74, 124, 89, 0.3);
}

.status-warning-terrasynapse {
    background: rgba(255, 152, 0, 0.1);
    color: #f57c00;
    border: 1px solid rgba(255, 152, 0, 0.3);
}

.status-error-terrasynapse {
    background: rgba(244, 67, 54, 0.1);
    color: #c62828;
    border: 1px solid rgba(244, 67, 54, 0.3);
}

/* Gráficos TerraSynapse */
.chart-container-terrasynapse {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(44, 85, 48, 0.08);
    margin: 1rem 0;
    border: 1px solid rgba(74, 124, 89, 0.1);
}

/* Footer TerraSynapse */
.footer-terrasynapse {
    text-align: center;
    padding: 2rem;
    color: #666;
    font-size: 0.9rem;
    border-top: 1px solid #e8f5e8;
    margin-top: 3rem;
    background: rgba(248, 255, 254, 0.8);
    backdrop-filter: blur(10px);
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

/* Loading TerraSynapse */
.loading-terrasynapse {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 3rem;
}

.spinner-terrasynapse {
    width: 40px;
    height: 40px;
    border: 4px solid #e8f5e8;
    border-top: 4px solid #4a7c59;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Responsivo */
@media (max-width: 768px) {
    .terrasynapse-header h1 {
        font-size: 2rem;
    }
    
    .terrasynapse-header p {
        font-size: 1rem;
    }
    
    .metric-value-terrasynapse {
        font-size: 2rem;
    }
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
            st.error(f"Erro na API: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        st.warning("Tempo limite excedido - API inicializando")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: {str(e)}")
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
    
    return -15.7942, -47.8822, "Brasília", "DF"

# Inicialização do estado da sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_token" not in st.session_state:
    st.session_state.user_token = None
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# Header TerraSynapse com Logo Correta
st.markdown("""
<div class="terrasynapse-header fade-in-up">
    <div class="logo-terrasynapse">
        <div class="logo-icon-terrasynapse">🌱</div>
        <div>
            <h1>TerraSynapse</h1>
            <p>Plataforma Enterprise de Monitoramento Agrícola</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar TerraSynapse
with st.sidebar:
    st.markdown("""
    <div class="sidebar-content-terrasynapse">
        <h2 style="color: #2c5530; margin-bottom: 1.5rem; font-weight: 600;">🔐 Portal Executivo</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["🔑 Login", "👤 Cadastro"])
        
        with tab1:
            st.markdown("<div class='sidebar-content-terrasynapse'>", unsafe_allow_html=True)
            st.subheader("Acesso Executivo")
            
            email = st.text_input("📧 Email Corporativo", key="login_email")
            password = st.text_input("🔒 Senha", type="password", key="login_password")
            
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
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with tab2:
            st.markdown("<div class='sidebar-content-terrasynapse'>", unsafe_allow_html=True)
            st.subheader("Registro Enterprise")
            
            nome = st.text_input("👤 Nome Completo", key="reg_nome")
            email_reg = st.text_input("📧 Email", key="reg_email")
            password_reg = st.text_input("🔒 Senha", type="password", key="reg_password")
            
            perfil = st.selectbox("🎯 Perfil Profissional", [
                "Produtor Rural", "Agrônomo", "Técnico Agrícola", 
                "Consultor", "Cooperativa", "Gerente Agrícola", "Outro"
            ])
            
            empresa = st.text_input("🏢 Empresa", key="reg_empresa")
            cidade = st.text_input("🌍 Cidade", key="reg_cidade")
            
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
                            st.error("❌ Erro no cadastro")
                else:
                    st.warning("⚠️ Preencha todos os campos obrigatórios")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    else:
        st.markdown(f"""
        <div class="sidebar-content-terrasynapse">
            <div style="text-align: center; padding: 1rem;">
                <div style="background: linear-gradient(135deg, #2c5530, #4a7c59); color: white; padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
                    <h3 style="margin: 0;">👋 Bem-vindo!</h3>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{st.session_state.user_data['nome']}</p>
                </div>
                <div class="status-indicator-terrasynapse status-online-terrasynapse">
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
    <div class="dashboard-section-terrasynapse fade-in-up">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <h3 style="margin: 0; color: #2c5530;">📍 Localização Detectada</h3>
                <p style="margin: 0.5rem 0 0 0; color: #666;">{cidade}, {estado} • {lat:.4f}, {lon:.4f}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 Atualizar Dados", type="primary"):
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("⚡ Auto-refresh (30s)")
    
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
        
        # Métricas principais TerraSynapse
        st.markdown("""
        <div class="dashboard-section-terrasynapse fade-in-up">
            <h2 class="section-title-terrasynapse">📊 Dashboard Executivo - Tempo Real</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card-terrasynapse">
                <div class="metric-container-terrasynapse">
                    <div style="color: #ff5722; font-size: 2rem;">🌡️</div>
                    <div class="metric-value-terrasynapse">{data["clima"]["temperatura"]}°C</div>
                    <div class="metric-label-terrasynapse">Temperatura</div>
                    <div class="metric-delta-terrasynapse">
                        Umidade: {data['clima']['umidade']}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            et0_color = "#c62828" if data["clima"]["et0"] > 6 else "#f57c00" if data["clima"]["et0"] > 4 else "#4a7c59"
            st.markdown(f"""
            <div class="metric-card-terrasynapse">
                <div class="metric-container-terrasynapse">
                    <div style="color: #2196f3; font-size: 2rem;">💧</div>
                    <div class="metric-value-terrasynapse" style="color: {et0_color};">{data["clima"]["et0"]}</div>
                    <div class="metric-label-terrasynapse">ET0 (mm/dia)</div>
                    <div class="metric-delta-terrasynapse">
                        {data['clima']['recomendacao_irrigacao']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            ndvi_color = data['vegetacao']['cor']
            st.markdown(f"""
            <div class="metric-card-terrasynapse">
                <div class="metric-container-terrasynapse">
                    <div style="color: #4a7c59; font-size: 2rem;">🌱</div>
                    <div class="metric-value-terrasynapse" style="color: {ndvi_color};">{data["vegetacao"]["ndvi"]}</div>
                    <div class="metric-label-terrasynapse">NDVI Índice</div>
                    <div class="metric-delta-terrasynapse">
                        {data['vegetacao']['status_vegetacao']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            receita = data["rentabilidade"]["receita_por_hectare"]
            st.markdown(f"""
            <div class="metric-card-terrasynapse">
                <div class="metric-container-terrasynapse">
                    <div style="color: #ff9800; font-size: 2rem;">💰</div>
                    <div class="metric-value-terrasynapse" style="color: #2c5530;">R$ {receita:,.0f}</div>
                    <div class="metric-label-terrasynapse">Receita/Hectare</div>
                    <div class="metric-delta-terrasynapse">
                        {data['rentabilidade']['produtividade_estimada']} sc/ha
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Sistema de Alertas TerraSynapse
        st.markdown("""
        <div class="dashboard-section-terrasynapse fade-in-up">
            <h2 class="section-title-terrasynapse">⚠️ Centro de Alertas Inteligentes</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if data["alertas"]:
            for alerta in data["alertas"]:
                if alerta["prioridade"] == "alta":
                    st.markdown(f"""
                    <div class="alert-terrasynapse alert-error-terrasynapse">
                        <strong>🚨 ALERTA CRÍTICO:</strong> {alerta['mensagem']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="alert-terrasynapse">
                        <strong>⚠️ ATENÇÃO:</strong> {alerta['mensagem']}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-terrasynapse alert-success-terrasynapse">
                <strong>✅ SISTEMA OPERACIONAL:</strong> Nenhum alerta crítico detectado.
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos TerraSynapse
        st.markdown("""
        <div class="dashboard-section-terrasynapse fade-in-up">
            <h2 class="section-title-terrasynapse">📈 Análise Técnica Avançada</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='chart-container-terrasynapse'>", unsafe_allow_html=True)
            
            # Gráfico ET0 TerraSynapse
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = data['clima']['et0'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Evapotranspiração (ET0)", 'font': {'size': 18, 'color': '#2c5530'}},
                delta = {'reference': 5},
                gauge = {
                    'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "#2c5530"},
                    'bar': {'color': "#4a7c59", 'thickness': 0.3},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e8f5e8",
                    'steps': [
                        {'range': [0, 3], 'color': "#f1f8e9"},
                        {'range': [3, 6], 'color': "#fff9e6"},
                        {'range': [6, 10], 'color': "#ffebee"}
                    ],
                    'threshold': {
                        'line': {'color': "#c62828", 'width': 4},
                        'thickness': 0.75,
                        'value': 6
                    }
                }
            ))
            
            fig_gauge.update_layout(
                height=300,
                font={'color': "#2c5530", 'family': "Inter"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='chart-container-terrasynapse'>", unsafe_allow_html=True)
            
            # Gráfico de commodities TerraSynapse
            commodities = data["mercado"]
            df_precos = pd.DataFrame([
                {
                    "Commodity": "Soja", 
                    "Preço": commodities["soja"]["preco"], 
                    "Variação": commodities["soja"]["variacao"]
                },
                {
                    "Commodity": "Milho", 
                    "Preço": commodities["milho"]["preco"], 
                    "Variação": commodities["milho"]["variacao"]
                },
                {
                    "Commodity": "Café", 
                    "Preço": commodities["cafe"]["preco"], 
                    "Variação": commodities["cafe"]["variacao"]
                }
            ])
            
            fig_bar = px.bar(
                df_precos, 
                x="Commodity", 
                y="Preço",
                color="Variação",
                color_continuous_scale=["#c62828", "#f57c00", "#4a7c59"],
                title="Commodities - Preços Atuais (R$/saca)"
            )
            
            fig_bar.update_traces(
                texttemplate='R$ %{y:.0f}',
                textposition='outside',
                marker_line_color='#2c5530',
                marker_line_width=1.5,
                opacity=0.8
            )
            
            fig_bar.update_layout(
                height=300,
                font={'color': "#2c5530", 'family': "Inter"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                title_font_size=16,
                title_font_color="#2c5530",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(44, 85, 48, 0.1)')
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Análise Detalhada TerraSynapse
        st.markdown("""
        <div class="dashboard-section-terrasynapse fade-in-up">
            <h2 class="section-title-terrasynapse">🔬 Análise Técnica Executiva</h2>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["🌡️ Climatologia", "🌱 Vegetação", "💰 Mercado"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="metric-card-terrasynapse">
                    <h4 style="color: #2c5530; margin-bottom: 1rem;">📊 Condições Meteorológicas</h4>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                    <div><strong>Temperatura:</strong> {data['clima']['temperatura']}°C</div>
                    <div><strong>Umidade:</strong> {data['clima']['umidade']}%</div>
                    <div><strong>Vento:</strong> {data['clima']['vento']} km/h</div>
                    <div><strong>Pressão:</strong> {data['clima']['pressao']} hPa</div>
                </div>
                <div style="margin-top: 1rem; padding: 1rem; background: #f1f8e9; border-radius: 8px;">
                    <strong>Condição:</strong> {data['clima']['descricao']}
                </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card-terrasynapse">
                    <h4 style="color: #2c5530; margin-bottom: 1rem;">💧 Gestão de Irrigação</h4>
                """, unsafe_allow_html=True)
                
                et0_status = "CRÍTICO" if data['clima']['et0'] > 6 else "MODERADO" if data['clima']['et0'] > 4 else "NORMAL"
                et0_color = "#c62828" if data['clima']['et0'] > 6 else "#f57c00" if data['clima']['et0'] > 4 else "#4a7c59"
                
                st.markdown(f"""
                <div style="margin: 1rem 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span><strong>ET0:</strong> {data['clima']['et0']} mm/dia</span>
                        <span style="color: {et0_color}; font-weight: bold;">{et0_status}</span>
                    </div>
                    <div style="background: #e8f5e8; height: 8px; border-radius: 4px;">
                        <div style="background: {et0_color}; height: 8px; width: {min(data['clima']['et0']/10*100, 100)}%; border-radius: 4px;"></div>
                    </div>
                </div>
                <div style="margin-top: 1rem; padding: 1rem; background: rgba(74, 124, 89, 0.1); border-left: 4px solid #4a7c59; border-radius: 4px;">
                    <strong>Recomendação:</strong> {data['clima']['recomendacao_irrigacao']}
                </div>
                </div>
                """, unsafe_allow_html=True)
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="metric-card-terrasynapse">
                    <h4 style="color: #2c5530; margin-bottom: 1rem;">🛰️ Análise NDVI</h4>
                """, unsafe_allow_html=True)
                
                ndvi_color = data['vegetacao']['cor']
                
                st.markdown(f"""
                <div style="text-align: center; margin: 1.5rem 0;">
                    <div style="background: {ndvi_color}; color: white; padding: 2rem; border-radius: 50%; width: 120px; height: 120px; margin: 0 auto; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 8px 24px rgba(74, 124, 89, 0.3);">
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
                <div class="metric-card-terrasynapse">
                    <h4 style="color: #2c5530; margin-bottom: 1rem;">📋 Recomendações Técnicas</h4>
                """, unsafe_allow_html=True)
                
                ndvi_val = data['vegetacao']['ndvi']
                if ndvi_val > 0.7:
                    status_icon = "🌟"
                    status_text = "Vegetação saudável e vigorosa"
                    status_color = "#4a7c59"
                elif ndvi_val > 0.5:
                    status_icon = "📈"
                    status_text = "Vegetação em desenvolvimento normal"
                    status_color = "#66bb6a"
                elif ndvi_val > 0.3:
                    status_icon = "📉"
                    status_text = "Vegetação com estresse moderado"
                    status_color = "#f57c00"
                else:
                    status_icon = "🚨"
                    status_text = "Vegetação em estado crítico"
                    status_color = "#c62828"
                
                st.markdown(f"""
                <div style="margin: 1rem 0; padding: 1.5rem; background: rgba(74, 124, 89, 0.1); border-left: 4px solid {status_color}; border-radius: 8px;">
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
            <div class="metric-card-terrasynapse">
                <h4 style="color: #2c5530; margin-bottom: 1.5rem;">📈 Análise de Mercado TerraSynapse</h4>
            </div>
            """, unsafe_allow_html=True)
            
            for commodity, info in data['mercado'].items():
                col1, col2, col3 = st.columns(3)
                
                trend_color = "#4a7c59" if info['variacao'] > 0 else "#c62828" if info['variacao'] < 0 else "#f57c00"
                trend_icon = "📈" if info['variacao'] > 0 else "📉" if info['variacao'] < 0 else "➡️"
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card-terrasynapse" style="text-align: center;">
                        <h5 style="color: #2c5530; margin-bottom: 0.5rem;">{commodity.title()}</h5>
                        <div style="font-size: 1.8rem; font-weight: bold; color: #2c5530;">R$ {info['preco']}</div>
                        <div style="font-size: 0.9rem; color: #666;">por saca</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card-terrasynapse" style="text-align: center;">
                        <div style="color: {trend_color}; font-size: 1.5rem; margin-bottom: 0.5rem;">{trend_icon}</div>
                        <div style="font-size: 1.2rem; font-weight: bold; color: {trend_color};">{info['variacao']:+.2f}%</div>
                        <div style="font-size: 0.9rem; color: #666;">variação</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    if commodity == "soja":
                        receita_estimada = info['preco'] * data['rentabilidade']['produtividade_estimada']
                        st.markdown(f"""
                        <div class="metric-card-terrasynapse" style="text-align: center;">
                            <div style="font-size: 1.2rem; font-weight: bold; color: #2c5530;">R$ {receita_estimada:,.0f}</div>
                            <div style="font-size: 0.9rem; color: #666;">receita/ha</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Calculadora de Rentabilidade TerraSynapse
        st.markdown("""
        <div class="dashboard-section-terrasynapse fade-in-up">
            <h2 class="section-title-terrasynapse">🧮 Calculadora Enterprise de Rentabilidade</h2>
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
            
            # Custos estimados
            custo_por_ha = 3000
            custo_total = area_ha * custo_por_ha
            lucro_total = receita_total - custo_total
            margem = (lucro_total / receita_total) * 100 if receita_total > 0 else 0
            
            st.markdown(f"""
            <div class="metric-card-terrasynapse">
                <h4 style="color: #2c5530; margin-bottom: 1rem;">💰 Projeção Financeira - {cultura_select}</h4>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin: 1.5rem 0;">
                    <div style="text-align: center; padding: 1rem; background: #f1f8e9; border-radius: 8px;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #2c5530;">R$ {receita_total:,.0f}</div>
                        <div style="color: #666; font-size: 0.9rem;">Receita Total</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: #fff9e6; border-radius: 8px;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #f57c00;">R$ {custo_total:,.0f}</div>
                        <div style="color: #666; font-size: 0.9rem;">Custo Estimado</div>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: #e8f5e8; border-radius: 8px;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #4a7c59;">R$ {lucro_total:,.0f}</div>
                        <div style="color: #666; font-size: 0.9rem;">Lucro Projetado</div>
                    </div>
                </div>
                
                <div style="margin-top: 1.5rem; padding: 1rem; background: #f1f8e9; border-radius: 8px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem; text-align: center;">
                        <div><strong>Área:</strong> {area_ha} ha</div>
                        <div><strong>Produtividade:</strong> {produtividade} sc/ha</div>
                        <div><strong>Preço:</strong> R$ {preco_cultura}/saca</div>
                        <div><strong>Margem:</strong> {margem:.1f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if receita_total > 200000:
                st.success("🎯 Excelente potencial de receita! Propriedade altamente rentável.")
            elif receita_total > 100000:
                st.info("📊 Boa projeção de receita. Considere otimizações para maximizar lucros.")
            else:
                st.warning("💡 Receita moderada. Analise possibilidades de aumento de produtividade.")
        
        # Footer TerraSynapse
        st.markdown(f"""
        <div class="footer-terrasynapse fade-in-up">
            <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
                <div>
                    <strong>TerraSynapse V2.0</strong> - Plataforma Enterprise de Monitoramento Agrícola
                </div>
                <div>
                    Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                </div>
                <div>
                    <span class="status-indicator-terrasynapse status-online-terrasynapse">
                        <span>🟢</span> Sistema Online
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div class="dashboard-section-terrasynapse">
            <div class="loading-terrasynapse">
                <div class="spinner-terrasynapse"></div>
            </div>
            <div style="text-align: center; color: #666;">
                <h3>🔄 Conectando com APIs Enterprise...</h3>
                <p>Aguarde enquanto sincronizamos os dados em tempo real</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Página inicial TerraSynapse
    st.markdown("""
    <div class="dashboard-section-terrasynapse fade-in-up">
        <div style="text-align: center; margin: 2rem 0;">
            <h2 style="color: #2c5530; margin-bottom: 2rem;">🌾 TerraSynapse V2.0 Enterprise</h2>
            <h3 style="color: #666; font-weight: 400; margin-bottom: 3rem;">Plataforma Líder em Inteligência Agrícola</h3>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 3rem 0;">
            <div class="metric-card-terrasynapse">
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🌡️</div>
                    <h4 style="color: #2c5530;">Monitoramento Climático</h4>
                    <p style="color: #666; line-height: 1.6;">Dados meteorológicos em tempo real com cálculo preciso de evapotranspiração e recomendações inteligentes de irrigação.</p>
                </div>
            </div>
            
            <div class="metric-card-terrasynapse">
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🛰️</div>
                    <h4 style="color: #2c5530;">Análise por Satélite</h4>
                    <p style="color: #666; line-height: 1.6;">Índices NDVI avançados para monitoramento da saúde vegetal com alertas automáticos de estresse.</p>
                </div>
            </div>
            
            <div class="metric-card-terrasynapse">
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">💰</div>
                    <h4 style="color: #2c5530;">Inteligência de Mercado</h4>
                    <p style="color: #666; line-height: 1.6;">Preços atualizados de commodities com análise de tendências e calculadora de rentabilidade.</p>
                </div>
            </div>
            
            <div class="metric-card-terrasynapse">
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                    <h4 style="color: #2c5530;">Dashboard Executivo</h4>
                    <p style="color: #666; line-height: 1.6;">Visão completa da propriedade com alertas inteligentes e relatórios automatizados.</p>
                </div>
            </div>
        </div>
        
        <div style="text-align: center; margin: 3rem 0;">
            <h3 style="color: #2c5530;">🚀 Pronto para Revolucionar sua Agricultura?</h3>
            <p style="color: #666; font-size: 1.1rem; margin: 1rem 0;">Faça login ou cadastre-se na barra lateral para acessar dados personalizados da sua propriedade.</p>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem; margin: 2rem 0;">
            <div style="text-align: center; padding: 1rem;">
                <div class="metric-value-terrasynapse" style="color: #4a7c59;">24.5°C</div>
                <div class="metric-label-terrasynapse">Temperatura Ideal</div>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div class="metric-value-terrasynapse" style="color: #2c5530;">0.75</div>
                <div class="metric-label-terrasynapse">NDVI Saudável</div>
            </div>
            <div style="text-align: center; padding: 1rem;">
                <div class="metric-value-terrasynapse" style="color: #4a7c59;">R$ 165.50</div>
                <div class="metric-label-terrasynapse">Soja (+2.3%)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Diagnóstico do Sistema TerraSynapse
if st.sidebar.button("🔧 Diagnóstico do Sistema", use_container_width=True):
    with st.spinner("🔄 Executando diagnóstico..."):
        health = fazer_requisicao("/health")
        if health:
            st.sidebar.success("✅ APIs TerraSynapse Online")
            st.sidebar.json(health)
        else:
            st.sidebar.error("❌ Sistema Temporariamente Indisponível")
