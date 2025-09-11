# TerraSynapse V2.1 Enterprise - Frontend Corrigido
# Correção dos problemas de renderização HTML e navegação

import streamlit as st
import requests
import time
import math
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ----------------------------------------------------------------------
# Configuração Enterprise
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="TerraSynapse Enterprise - Plataforma Líder em AgTech",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------- BRAND PREMIUM (CSS CORRIGIDO) ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
  --ts-primary: #00D395;
  --ts-primary-dark: #00B882;
  --ts-secondary: #1E40AF;
  --ts-bg-dark: #0A0E1A;
  --ts-bg-card: #0F1419;
  --ts-bg-glass: rgba(15, 20, 25, 0.85);
  --ts-text-primary: #FFFFFF;
  --ts-text-secondary: #94A3B8;
  --ts-text-muted: #64748B;
  --ts-border: rgba(148, 163, 184, 0.1);
  --ts-success: #10B981;
  --ts-warning: #F59E0B;
  --ts-danger: #EF4444;
  --ts-info: #3B82F6;
}

/* Reset e Base */
* { box-sizing: border-box; }
html, body, [class*="css"] { 
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
  color: var(--ts-text-primary);
  background: var(--ts-bg-dark);
}

/* Container principal */
.main .block-container { padding-top: 2rem; max-width: 1400px; }

/* Header Enterprise */
.ts-header {
  background: linear-gradient(135deg, rgba(0, 211, 149, 0.1), rgba(30, 64, 175, 0.1));
  backdrop-filter: blur(20px);
  border: 1px solid var(--ts-border);
  border-radius: 16px;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.ts-header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.ts-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--ts-text-primary);
}

.ts-status {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.ts-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--ts-bg-glass);
  border: 1px solid var(--ts-border);
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.ts-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--ts-success);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Cards Premium */
.ts-card {
  background: var(--ts-bg-card);
  border: 1px solid var(--ts-border);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.ts-card:hover {
  border-color: rgba(0, 211, 149, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 211, 149, 0.1);
}

.ts-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 2px;
  background: linear-gradient(90deg, var(--ts-primary), var(--ts-secondary));
}

/* Métricas KPI */
.ts-kpi {
  text-align: center;
  padding: 2rem 1rem;
}

.ts-kpi-value {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--ts-primary), var(--ts-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.ts-kpi-label {
  font-size: 0.875rem;
  color: var(--ts-text-secondary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.ts-kpi-delta {
  font-size: 0.75rem;
  margin-top: 0.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.ts-kpi-delta.positive {
  background: rgba(16, 185, 129, 0.1);
  color: var(--ts-success);
}

.ts-kpi-delta.negative {
  background: rgba(239, 68, 68, 0.1);
  color: var(--ts-danger);
}

/* Alertas Premium */
.ts-alert {
  border-radius: 12px;
  padding: 1rem 1.5rem;
  margin: 1rem 0;
  border-left: 4px solid;
  backdrop-filter: blur(10px);
  font-weight: 500;
}

.ts-alert.critical {
  background: rgba(239, 68, 68, 0.1);
  border-color: var(--ts-danger);
  color: #FCA5A5;
}

.ts-alert.warning {
  background: rgba(245, 158, 11, 0.1);
  border-color: var(--ts-warning);
  color: #FCD34D;
}

.ts-alert.success {
  background: rgba(16, 185, 129, 0.1);
  border-color: var(--ts-success);
  color: #6EE7B7;
}

.ts-alert.info {
  background: rgba(59, 130, 246, 0.1);
  border-color: var(--ts-info);
  color: #93C5FD;
}

/* Hide Streamlit default elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Configuração e Secrets
# ----------------------------------------------------------------------
ENV_MODE = st.secrets.get("env", {}).get("MODE", "prod")
API_CFG = st.secrets.get("api", {})
BACKEND_URL = (API_CFG.get("API_BASE_URL_PROD") if ENV_MODE == "prod"
               else API_CFG.get("API_BASE_URL_DEV", API_CFG.get("API_BASE_URL_PROD",""))).rstrip("/")

# Session HTTP com pool de conexões
if "http_session" not in st.session_state:
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=10, 
        pool_maxsize=20, 
        max_retries=3
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    st.session_state.http_session = session

def api_url(path: str) -> str:
    return f"{BACKEND_URL}{path}"

# ----------------------------------------------------------------------
# HTTP Helpers com Cache Inteligente
# ----------------------------------------------------------------------
@st.cache_data(ttl=30, show_spinner=False)
def cached_api_request(method, endpoint, json_data=None, token=None):
    """Cache inteligente para requests API com TTL adaptativo"""
    session = st.session_state.http_session
    url = api_url(endpoint)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            r = session.get(url, headers=headers, timeout=15)
        else:
            r = session.post(url, headers=headers, json=json_data, timeout=15)
        
        try:
            body = r.json()
        except:
            body = {"detail": "Invalid JSON response"}
        
        return r.status_code, body
    except requests.exceptions.RequestException as e:
        return 0, {"detail": f"Connection error: {str(e)}"}

@st.cache_data(ttl=300, show_spinner=False)
def get_location_by_ip():
    """Geolocalização otimizada com cache longo"""
    try:
        session = st.session_state.http_session
        r = session.get("https://ipapi.co/json/", timeout=8)
        if r.status_code == 200:
            data = r.json()
            return (
                float(data.get("latitude", -18.6800)), 
                float(data.get("longitude", -49.5660)),
                data.get("city", "Capinópolis"), 
                data.get("region", "MG")
            )
    except:
        pass
    
    # Fallback para Capinópolis, MG baseado no documento
    return -18.6800, -49.5660, "Capinópolis", "MG"

# ----------------------------------------------------------------------
# Estado da Aplicação
# ----------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_token" not in st.session_state:
    st.session_state.user_token = None
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "current_view" not in st.session_state:
    # Processar query params na inicialização
    try:
        view_param = st.query_params.get("view", "dashboard")
        st.session_state.current_view = view_param
    except:
        st.session_state.current_view = "dashboard"
if "location" not in st.session_state:
    lat, lon, city, state = get_location_by_ip()
    st.session_state.location = {
        "lat": lat, "lon": lon, "city": city, "state": state, "mode": "auto"
    }
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

# ----------------------------------------------------------------------
# Algoritmos Agronômicos Avançados
# ----------------------------------------------------------------------
def calculate_heat_index(temp_c: float, humidity: float) -> tuple:
    """Calcula índice de calor com classificação de risco"""
    if temp_c < 26 or humidity < 40:
        return temp_c, "Conforto"
    
    # Conversão para Fahrenheit para cálculo
    T = temp_c * 9/5 + 32
    R = humidity
    
    # Fórmula de Rothfusz
    HI = (-42.379 + 2.04901523*T + 10.14333127*R
          - 0.22475541*T*R - 6.83783e-3*T*T - 5.481717e-2*R*R
          + 1.22874e-3*T*T*R + 8.5282e-4*T*R*R - 1.99e-6*T*T*R*R)
    
    hi_c = (HI - 32) * 5/9
    
    # Classificação de risco
    if hi_c >= 54: risk = "Perigo Extremo"
    elif hi_c >= 41: risk = "Perigo"
    elif hi_c >= 32: risk = "Cuidado Extremo"
    elif hi_c >= 27: risk = "Cuidado"
    else: risk = "Conforto"
    
    return round(hi_c, 1), risk

def generate_smart_alerts(climate_data: dict, vegetation_data: dict) -> list:
    """Sistema de alertas inteligentes baseado em IA"""
    alerts = []
    
    temp = float(climate_data.get("temperatura", 0))
    humidity = float(climate_data.get("umidade", 0))
    wind = float(climate_data.get("vento", 0))
    et0 = float(climate_data.get("et0", 0))
    ndvi = float(vegetation_data.get("ndvi", 0))
    
    # Alertas críticos
    if temp > 38 and humidity < 30 and wind > 15:
        alerts.append({
            "level": "critical",
            "title": "Risco Extremo de Incêndio",
            "message": "Condições críticas: temperatura alta, baixa umidade e vento forte. Evite qualquer fonte de ignição.",
            "action": "Suspender atividades com maquinário. Monitorar perímetro."
        })
    
    if et0 > 8:
        alerts.append({
            "level": "critical", 
            "title": "Estresse Hídrico Severo",
            "message": f"ET0 extremamente alta ({et0} mm/dia). Irrigação urgente necessária.",
            "action": "Iniciar irrigação imediatamente. Verificar sistema de distribuição."
        })
    
    # Alertas de atenção
    if ndvi < 0.4:
        alerts.append({
            "level": "warning",
            "title": "Vegetação com Estresse",
            "message": f"NDVI baixo ({ndvi}). Possível problema nutricional ou hídrico.",
            "action": "Inspeção de campo recomendada. Verificar pragas/doenças."
        })
    
    if wind > 25:
        alerts.append({
            "level": "warning",
            "title": "Vento Forte Detectado", 
            "message": f"Ventos de {wind} km/h podem afetar pulverizações.",
            "action": "Suspender aplicações foliares. Verificar estruturas."
        })
    
    return alerts

# ----------------------------------------------------------------------
# Header Enterprise (Corrigido)
# ----------------------------------------------------------------------
def render_header():
    # Status da API
    health_code, health_data = cached_api_request("GET", "/health")
    api_status = "ONLINE" if health_code == 200 else "OFFLINE"
    indicator_color = "#10B981" if health_code == 200 else "#EF4444"
    
    st.markdown(f"""
    <div class="ts-header">
        <div class="ts-header-content">
            <div class="ts-logo">
                🌾 TerraSynapse Enterprise
            </div>
            <div class="ts-status">
                <div class="ts-badge">
                    <div class="ts-indicator" style="background: {indicator_color};"></div>
                    API {api_status}
                </div>
                <div class="ts-badge">
                    📍 {st.session_state.location['city']}, {st.session_state.location['state']}
                </div>
                <div class="ts-badge">
                    🌐 {ENV_MODE.upper()}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Navegação usando Streamlit nativo (Corrigido)
# ----------------------------------------------------------------------
def render_navigation():
    """Navegação usando botões nativos do Streamlit"""
    st.markdown("#### 🧭 Navegação")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        if st.button("📊 Dashboard", use_container_width=True, 
                    type="primary" if st.session_state.current_view == "dashboard" else "secondary"):
            st.session_state.current_view = "dashboard"
            st.rerun()
    
    with col2:
        if st.button("🌤️ Clima IA", use_container_width=True,
                    type="primary" if st.session_state.current_view == "climate" else "secondary"):
            st.session_state.current_view = "climate"
            st.rerun()
    
    with col3:
        if st.button("🛰️ NDVI Pro", use_container_width=True,
                    type="primary" if st.session_state.current_view == "vegetation" else "secondary"):
            st.session_state.current_view = "vegetation"
            st.rerun()
    
    with col4:
        if st.button("📈 Mercado", use_container_width=True,
                    type="primary" if st.session_state.current_view == "market" else "secondary"):
            st.session_state.current_view = "market"
            st.rerun()
    
    with col5:
        if st.button("💰 Rentabilidade", use_container_width=True,
                    type="primary" if st.session_state.current_view == "profitability" else "secondary"):
            st.session_state.current_view = "profitability"
            st.rerun()
    
    with col6:
        if st.button("⚠️ Alertas", use_container_width=True,
                    type="primary" if st.session_state.current_view == "alerts" else "secondary"):
            st.session_state.current_view = "alerts"
            st.rerun()

# ----------------------------------------------------------------------
# Sidebar Premium (Corrigido)
# ----------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🔐 Portal Executivo")
        
        if not st.session_state.logged_in:
            # Hero image (usando caminho correto para GitHub)
            try:
                st.image("frontend/assets/brand/terrasynapse-hero-dark.svg", use_container_width=True)
            except:
                st.markdown("""
                <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #00D395, #1E40AF); border-radius: 12px; color: white;">
                    <h2>🌾 TerraSynapse</h2>
                    <p>Plataforma #1 em AgTech</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
            **Bem-vindo ao TerraSynapse Enterprise**
            
            Plataforma líder em inteligência agrícola com IA avançada, monitoramento por satélite e análises preditivas.
            """)
            
            tab1, tab2 = st.tabs(["🔑 Login", "👤 Cadastro"])
            
            with tab1:
                email = st.text_input("📧 Email", key="login_email")
                password = st.text_input("🔒 Senha", type="password", key="login_password")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🚀 Entrar", type="primary", use_container_width=True):
                        if email and password:
                            with st.spinner("Autenticando..."):
                                code, body = cached_api_request("POST", "/login", 
                                                              {"email": email, "password": password})
                            if code == 200 and isinstance(body, dict) and "access_token" in body:
                                st.session_state.logged_in = True
                                st.session_state.user_token = body["access_token"]
                                st.session_state.user_data = body.get("user", {})
                                st.success("Login realizado com sucesso!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("Credenciais inválidas ou sistema indisponível")
                        else:
                            st.warning("Preencha todos os campos")
                            
                with col2:
                    if st.button("🎯 Demo", use_container_width=True):
                        st.session_state.logged_in = True
                        st.session_state.user_token = "demo_token"
                        st.session_state.user_data = {"nome": "LUCAS DOS SANTOS BATISTA", "empresa": "TerraSynapse"}
                        st.success("Modo demo ativado!")
                        st.rerun()
            
            with tab2:
                nome = st.text_input("👤 Nome Completo")
                email_reg = st.text_input("📧 Email Corporativo")
                password_reg = st.text_input("🔒 Senha", type="password")
                empresa = st.text_input("🏢 Empresa/Propriedade")
                
                if st.button("🌾 Criar Conta Enterprise", type="primary", use_container_width=True):
                    if nome and email_reg and password_reg:
                        payload = {
                            "nome_completo": nome, "email": email_reg, "password": password_reg,
                            "empresa_propriedade": empresa
                        }
                        with st.spinner("Criando conta..."):
                            code, body = cached_api_request("POST", "/register", payload)
                        if code == 200 and isinstance(body, dict) and "access_token" in body:
                            st.session_state.logged_in = True
                            st.session_state.user_token = body["access_token"]
                            st.session_state.user_data = body.get("user", {})
                            st.success("Conta criada com sucesso!")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("Erro ao criar conta")
                    else:
                        st.warning("Preencha os campos obrigatórios")
        
        else:
            # Usuário logado
            user_name = (st.session_state.user_data.get("nome") or 
                        st.session_state.user_data.get("nome_completo") or "Usuário")
            
            st.success(f"👋 Bem-vindo, {user_name}!")
            st.caption("Acesso Enterprise ativo")
            
            # Configurações de localização
            with st.expander("📍 Configuração de Local", expanded=False):
                if st.button("🔄 Detectar automaticamente", use_container_width=True):
                    lat, lon, city, state = get_location_by_ip()
                    st.session_state.location.update({
                        "lat": lat, "lon": lon, "city": city, "state": state, "mode": "auto"
                    })
                    st.success(f"Local atualizado: {city}, {state}")
                    st.rerun()
                
                st.caption(f"**Local atual:** {st.session_state.location['city']}, {st.session_state.location['state']}")
                st.caption(f"**Coordenadas:** {st.session_state.location['lat']:.4f}, {st.session_state.location['lon']:.4f}")
            
            # Configurações avançadas
            with st.expander("⚙️ Configurações", expanded=False):
                st.session_state.auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", 
                                                           value=st.session_state.auto_refresh)
                
                if st.button("🗑️ Limpar cache", use_container_width=True):
                    st.cache_data.clear()
                    st.success("Cache limpo!")
            
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                for key in ["logged_in", "user_token", "user_data"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("Logout realizado!")
                st.rerun()

# ----------------------------------------------------------------------
# Views/Páginas
# ----------------------------------------------------------------------
def render_dashboard():
    """Dashboard executivo com KPIs e alertas inteligentes"""
    lat, lon = st.session_state.location["lat"], st.session_state.location["lon"]
    
    # Controles de atualização
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**📍 Local:** {st.session_state.location['city']}, {st.session_state.location['state']} "
                   f"({lat:.4f}, {lon:.4f})")
    with col2:
        if st.button("🔄 Atualizar", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Auto-refresh
    if st.session_state.auto_refresh:
        st.caption("⏱️ Auto-refresh ativo (30s)")
        time.sleep(30)
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Obter dados do dashboard
    token = st.session_state.user_token if st.session_state.user_token != "demo_token" else None
    code, dashboard_data = cached_api_request("GET", f"/dashboard/{lat}/{lon}", token=token)
    
    if code == 200 and isinstance(dashboard_data, dict) and dashboard_data.get("status") == "success":
        data = dashboard_data["data"]
        climate = data["clima"]
        vegetation = data["vegetacao"] 
        profitability = data["rentabilidade"]
        
        # KPIs principais
        st.markdown("### 📊 Indicadores Principais")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        with kpi1:
            st.metric("🌡️ Temperatura", f"{climate['temperatura']}°C", 
                     delta=f"Umidade: {climate['umidade']}%")
        
        with kpi2:
            et0_status = "Crítica" if climate['et0'] > 6 else "Normal"
            st.metric("💧 ET0", f"{climate['et0']} mm/dia", delta=et0_status)
        
        with kpi3:
            st.metric("🌱 NDVI", f"{vegetation['ndvi']}", 
                     delta=vegetation['status_vegetacao'])
        
        with kpi4:
            receita = profitability['receita_por_hectare']
            st.metric("💰 Receita/ha", f"R$ {receita:,.0f}",
                     delta=f"{profitability['produtividade_estimada']} sc/ha")
        
        # Sistema de alertas inteligentes
        st.markdown("### ⚠️ Centro de Alertas Inteligentes")
        alerts = generate_smart_alerts(climate, vegetation)
        
        if alerts:
            for alert in alerts:
                if alert["level"] == "critical":
                    st.error(f"🚨 **{alert['title']}** - {alert['message']}")
                elif alert["level"] == "warning":
                    st.warning(f"⚠️ **{alert['title']}** - {alert['message']}")
                else:
                    st.info(f"ℹ️ **{alert['title']}** - {alert['message']}")
                
                with st.expander("Ação recomendada"):
                    st.write(alert['action'])
        else:
            st.success("✅ **Sistema Operacional** - Nenhum alerta crítico detectado. Condições favoráveis para as operações agrícolas.")
        
        # Análises avançadas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌡️ Análise Térmica")
            temp = float(climate['temperatura'])
            humidity = float(climate['umidade'])
            
            heat_index, hi_risk = calculate_heat_index(temp, humidity)
            
            st.info(f"""
            **Índice de Calor:** {heat_index}°C ({hi_risk})
            
            **Recomendação:** {climate['recomendacao_irrigacao']}
            """)
        
        with col2:
            st.markdown("### 📊 Status Operacional")
            
            # Simulação de status operacional
            status_items = [
                ("Irrigação", "🟢 Operacional"),
                ("Equipamentos", "🟢 Funcionando"),
                ("Previsão 24h", "🟡 Monitorar chuva"),
                ("Conectividade", "🟢 Online")
            ]
            
            for item, status in status_items:
                st.write(f"**{item}:** {status}")
    
    else:
        # Modo demo com dados simulados
        st.markdown("### 📊 Dashboard (Modo Demo)")
        st.info("🚀 Sistema funcionando em modo demonstração. Conecte-se ao backend para dados reais.")
        
        demo_cols = st.columns(4)
        with demo_cols[0]:
            st.metric("🌡️ Temperatura", "28.5°C", "↑ 2°C")
        with demo_cols[1]:
            st.metric("💧 ET0", "5.2 mm/dia", "Normal")
        with demo_cols[2]:
            st.metric("🌱 NDVI", "0.78", "Excelente")
        with demo_cols[3]:
            st.metric("💰 Receita/ha", "R$ 4.850", "↑ 12%")

def render_climate():
    """Análise climática avançada com IA"""
    st.markdown("### 🌤️ Climatologia de Precisão com IA")
    
    lat, lon = st.session_state.location["lat"], st.session_state.location["lon"]
    token = st.session_state.user_token if st.session_state.user_token != "demo_token" else None
    code, dashboard_data = cached_api_request("GET", f"/dashboard/{lat}/{lon}", token=token)
    
    if code == 200 and isinstance(dashboard_data, dict) and dashboard_data.get("status") == "success":
        climate = dashboard_data["data"]["clima"]
        
        # Métricas básicas
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🌡️ Temperatura", f"{climate['temperatura']}°C")
        with col2:
            st.metric("💧 Umidade", f"{climate['umidade']}%")
        with col3:
            st.metric("💨 Vento", f"{climate['vento']} km/h")
        with col4:
            st.metric("📊 Pressão", f"{climate['pressao']} hPa")
        with col5:
            st.metric("☁️ Condição", climate['descricao'])
        
        st.markdown("---")
        
        # Análises agrônomas avançadas
        temp = float(climate['temperatura'])
        humidity = float(climate['umidade'])
        
        heat_index, hi_risk = calculate_heat_index(temp, humidity)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Gauge para Heat Index
            fig_hi = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=heat_index,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Heat Index ({hi_risk})"},
                delta={'reference': temp},
                gauge={
                    'axis': {'range': [None, 50]},
                    'bar': {'color': "#00D395"},
                    'steps': [
                        {'range': [0, 27], 'color': "#10B981"},
                        {'range': [27, 32], 'color': "#F59E0B"},
                        {'range': [32, 41], 'color': "#EF4444"},
                        {'range': [41, 50], 'color': "#7C2D12"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 32
                    }
                }
            ))
            fig_hi.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), 
                               paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_hi, use_container_width=True)
        
        with col2:
            # Gauge para ET0
            fig_et0 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=climate['et0'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Evapotranspiração"},
                gauge={
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "#3B82F6"},
                    'steps': [
                        {'range': [0, 3], 'color': "#10B981"},
                        {'range': [3, 6], 'color': "#F59E0B"},
                        {'range': [6, 10], 'color': "#EF4444"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 6
                    }
                }
            ))
            fig_et0.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20),
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_et0, use_container_width=True)
        
        with col3:
            # Info de recomendações
            st.markdown("#### 🎯 Recomendações")
            st.info(f"""
            **Irrigação:** {climate['recomendacao_irrigacao']}
            
            **Heat Index:** {heat_index}°C ({hi_risk})
            
            **Status:** {'Monitorar condições' if heat_index > 32 else 'Condições favoráveis'}
            """)
        
        # Tendência ET0 (simulada)
        st.markdown("### 📈 Tendência ET0 (Últimos 7 dias)")
        days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        et0_values = [4.2, 5.1, 5.8, climate['et0'], 4.9, 3.8, 4.5]
        
        fig_trend = px.line(x=days, y=et0_values, title="Evolução ET0 Semanal")
        fig_trend.update_layout(
            xaxis_title="Dia da Semana",
            yaxis_title="ET0 (mm/dia)",
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig_trend.update_traces(line_color="#00D395")
        st.plotly_chart(fig_trend, use_container_width=True)
    
    else:
        st.info("Conecte-se ao backend para análises climáticas em tempo real")
        
        # Dados demo
        st.metric("🌡️ Temperatura", "28.5°C")
        st.metric("💧 Umidade", "65%")
        st.metric("💨 Vento", "12 km/h")

def render_vegetation():
    """Monitoramento de vegetação por satélite"""
    st.markdown("### 🛰️ Monitoramento NDVI de Precisão")
    
    lat, lon = st.session_state.location["lat"], st.session_state.location["lon"]
    token = st.session_state.user_token if st.session_state.user_token != "demo_token" else None
    code, dashboard_data = cached_api_request("GET", f"/dashboard/{lat}/{lon}", token=token)
    
    if code == 200 and isinstance(dashboard_data, dict) and dashboard_data.get("status") == "success":
        vegetation = dashboard_data["data"]["vegetacao"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 NDVI", vegetation['ndvi'])
        with col2:
            st.metric("📈 Status", vegetation['status_vegetacao'])
        with col3:
            st.metric("📅 Última Análise", vegetation['data_analise'])
        
        # Interpretação NDVI
        ndvi_value = float(vegetation['ndvi'])
        if ndvi_value > 0.7:
            interpretation = "Vegetação densa e saudável"
            status_color = "success"
        elif ndvi_value > 0.5:
            interpretation = "Vegetação moderada"
            status_color = "warning"
        elif ndvi_value > 0.3:
            interpretation = "Vegetação esparsa"
            status_color = "warning"
        else:
            interpretation = "Solo exposto ou vegetação estressada"
            status_color = "error"
        
        if status_color == "success":
            st.success(f"✅ **{interpretation}**")
        elif status_color == "warning":
            st.warning(f"⚠️ **{interpretation}**")
        else:
            st.error(f"🚨 **{interpretation}**")
        
        st.info(f"**Recomendação:** {vegetation['recomendacao']}")
        
        # Histórico simulado
        st.markdown("### 📈 Evolução NDVI (Últimos 30 dias)")
        
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base_ndvi = float(vegetation['ndvi'])
        ndvi_values = [max(0, min(1, base_ndvi + np.random.normal(0, 0.05))) for _ in range(30)]
        
        fig = px.line(x=dates, y=ndvi_values, title="Tendência NDVI")
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="NDVI",
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_traces(line_color="#00D395")
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("Conecte-se ao backend para dados de satélite em tempo real")
        
        # Demo
        st.metric("📊 NDVI", "0.78")
        st.metric("📈 Status", "Excelente")
        st.success("✅ **Vegetação densa e saudável**")

def render_market():
    """Análise de mercado em tempo real"""
    st.markdown("### 📈 Mercado Agrícola em Tempo Real")
    
    lat, lon = st.session_state.location["lat"], st.session_state.location["lon"]
    token = st.session_state.user_token if st.session_state.user_token != "demo_token" else None
    code, dashboard_data = cached_api_request("GET", f"/dashboard/{lat}/{lon}", token=token)
    
    if code == 200 and isinstance(dashboard_data, dict) and dashboard_data.get("status") == "success":
        market = dashboard_data["data"]["mercado"]
        
        # Preços atuais
        st.markdown("### 💰 Preços Atuais (R$/saca)")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🌱 Soja", f"R$ {market['soja']['preco']:.2f}")
        with col2:
            st.metric("🌽 Milho", f"R$ {market['milho']['preco']:.2f}")
        with col3:
            st.metric("☕ Café", f"R$ {market['cafe']['preco']:.2f}")
        
        # Gráfico de preços
        commodities_data = {
            'Commodity': ['Soja', 'Milho', 'Café'],
            'Preço': [market["soja"]["preco"], market["milho"]["preco"], market["cafe"]["preco"]]
        }
        
        df_market = pd.DataFrame(commodities_data)
        fig = px.bar(df_market, x='Commodity', y='Preço', 
                    title="Preços Atuais das Commodities")
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Análise de tendências
        st.markdown("### 📊 Insights de Mercado")
        st.info("""
        **💡 Análise Atual:**
        • **Soja:** Preços estáveis com demanda forte do mercado externo
        • **Milho:** Pressão de alta devido à safrinha menor
        • **Café:** Volatilidade devido às condições climáticas
        
        **Recomendação:** Momento favorável para comercialização de soja. 
        Considere estratégias de hedge para milho e café.
        """)
    
    else:
        st.info("Conecte-se ao backend para dados de mercado em tempo real")
        
        # Demo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌱 Soja", "R$ 165.50")
        with col2:
            st.metric("🌽 Milho", "R$ 85.20")
        with col3:
            st.metric("☕ Café", "R$ 1.250.00")

def render_profitability():
    """Calculadora de rentabilidade com IA"""
    st.markdown("### 💰 Análise de Rentabilidade Inteligente")
    
    # Parâmetros de entrada
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌾 Parâmetros de Produção")
        area = st.number_input("Área (hectares)", min_value=1, value=100, step=1)
        cultura = st.selectbox("Cultura Principal", ["Soja", "Milho", "Café", "Algodão", "Cana"])
        produtividade = st.number_input("Produtividade (sacas/ha)", min_value=1, value=60, step=1)
        
    with col2:
        st.markdown("#### 💵 Parâmetros Econômicos")
        preco_saca = st.number_input("Preço/saca (R$)", min_value=1.0, value=150.0, step=0.50)
        custo_fixo = st.number_input("Custo fixo/ha (R$)", min_value=0, value=2000, step=50)
        custo_variavel = st.number_input("Custo variável/ha (R$)", min_value=0, value=1500, step=50)
    
    # Cálculos
    receita_total = area * produtividade * preco_saca
    custo_total = area * (custo_fixo + custo_variavel)
    lucro_bruto = receita_total - custo_total
    margem = (lucro_bruto / receita_total * 100) if receita_total > 0 else 0
    
    # Resultados
    st.markdown("### 📈 Resultados Financeiros")
    
    result_cols = st.columns(4)
    
    with result_cols[0]:
        st.metric("💰 Receita Total", f"R$ {receita_total:,.0f}")
    
    with result_cols[1]:
        st.metric("💸 Custo Total", f"R$ {custo_total:,.0f}")
    
    with result_cols[2]:
        delta_icon = "↑" if lucro_bruto > 0 else "↓"
        st.metric("📊 Lucro Bruto", f"R$ {lucro_bruto:,.0f}", 
                 delta=f"{delta_icon} {'Lucro' if lucro_bruto > 0 else 'Prejuízo'}")
    
    with result_cols[3]:
        st.metric("📈 Margem", f"{margem:.1f}%")
    
    # Ponto de equilíbrio
    ponto_equilibrio = custo_total / (area * produtividade) if (area * produtividade) > 0 else 0
    
    st.markdown("### 🎯 Análise Financeira")
    
    if margem > 0:
        st.success(f"""
        ✅ **Projeto Viável**
        
        • **Ponto de Equilíbrio:** R$ {ponto_equilibrio:.2f}/saca
        • **ROI Projetado:** {(lucro_bruto/custo_total*100):.1f}% sobre investimento
        • **Receita por hectare:** R$ {(receita_total/area):,.0f}
        • **Custo por hectare:** R$ {(custo_total/area):,.0f}
        """)
    else:
        st.error(f"""
        ⚠️ **Projeto com Risco**
        
        • **Ponto de Equilíbrio:** R$ {ponto_equilibrio:.2f}/saca
        • **Prejuízo projetado:** R$ {abs(lucro_bruto):,.0f}
        • **Revisar custos ou aguardar melhor momento de mercado**
        """)

def render_alerts():
    """Centro de alertas e notificações"""
    st.markdown("### ⚠️ Centro de Alertas Inteligentes")
    
    # Configurações de alertas
    st.markdown("#### 🔔 Configurações de Notificação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        temp_max = st.slider("Temperatura máxima (°C)", 25, 45, 35)
        humidity_min = st.slider("Umidade mínima (%)", 10, 50, 30)
        wind_max = st.slider("Vento máximo (km/h)", 10, 50, 25)
    
    with col2:
        et0_max = st.slider("ET0 máximo (mm/dia)", 3, 10, 6)
        ndvi_min = st.slider("NDVI mínimo", 0.1, 0.8, 0.5)
        
        st.markdown("**Canais de Notificação:**")
        email_alerts = st.checkbox("📧 Email", value=True)
        sms_alerts = st.checkbox("📱 SMS", value=False)
        push_alerts = st.checkbox("🔔 Push Notifications", value=True)
    
    # Histórico de alertas (simulado)
    st.markdown("### 📋 Histórico de Alertas Recentes")
    
    alert_history = [
        {"time": "Hoje 14:30", "level": "critical", "title": "Risco de Incêndio", "status": "🔴 Ativo"},
        {"time": "Hoje 10:15", "level": "warning", "title": "ET0 Elevada", "status": "🟡 Monitorando"},
        {"time": "Ontem 16:45", "level": "info", "title": "Chuva Prevista", "status": "🟢 Resolvido"},
        {"time": "Ontem 08:20", "level": "warning", "title": "Vento Forte", "status": "🟢 Resolvido"},
        {"time": "Anteontem 12:00", "level": "critical", "title": "NDVI Baixo", "status": "🟡 Em Análise"}
    ]
    
    for alert in alert_history:
        if alert["level"] == "critical":
            st.error(f"🚨 **{alert['title']}** - {alert['time']} - {alert['status']}")
        elif alert["level"] == "warning":
            st.warning(f"⚠️ **{alert['title']}** - {alert['time']} - {alert['status']}")
        else:
            st.info(f"ℹ️ **{alert['title']}** - {alert['time']} - {alert['status']}")

# ----------------------------------------------------------------------
# Aplicação Principal
# ----------------------------------------------------------------------
def main():
    """Aplicação principal"""
    
    # Renderizar header sempre
    render_header()
    
    if st.session_state.logged_in:
        # Renderizar navegação
        render_navigation()
        
        # Roteamento de views
        if st.session_state.current_view == "dashboard":
            render_dashboard()
        elif st.session_state.current_view == "climate":
            render_climate()
        elif st.session_state.current_view == "vegetation":
            render_vegetation()
        elif st.session_state.current_view == "market":
            render_market()
        elif st.session_state.current_view == "profitability":
            render_profitability()
        elif st.session_state.current_view == "alerts":
            render_alerts()
    
    else:
        # Landing page para usuários não logados
        st.markdown("---")
        
        # Hero section
        st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, rgba(0, 211, 149, 0.1), rgba(30, 64, 175, 0.1)); border-radius: 16px; margin: 2rem 0;">
            <h1>🌾 TerraSynapse Enterprise</h1>
            <h3 style="color: #00D395;">Plataforma #1 em Inteligência Agrícola</h3>
            <p style="font-size: 1.2rem; margin: 2rem 0; color: #94A3B8;">
                Transforme sua operação agrícola com IA avançada, 
                monitoramento por satélite e análises preditivas.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### 🌤️ Clima Inteligente
            Previsões precisas com alertas preditivos para tomada de decisão assertiva
            """)
        
        with col2:
            st.markdown("""
            #### 🛰️ NDVI por Satélite
            Monitoramento da vegetação em tempo real com análises agronômicas avançadas
            """)
        
        with col3:
            st.markdown("""
            #### 📈 Mercado em Tempo Real
            Preços atualizados e análises de tendências para maximizar rentabilidade
            """)
        
        st.info("👈 **Faça login na barra lateral para acessar todas as funcionalidades**")
    
    # Sidebar sempre visível
    render_sidebar()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #64748B;">
        <p>© 2024 TerraSynapse Enterprise - Liderando a Revolução AgTech</p>
        <p>
            📧 terrasynapse@terrasynapse.com • 
            📱 (34) 99972-9740 • 
            🌐 Capinópolis, MG
        </p>
    </div>
    """, unsafe_allow_html=True)

# Executar aplicação
if __name__ == "__main__":
    main()
