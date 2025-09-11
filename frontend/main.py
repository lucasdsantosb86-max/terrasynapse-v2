# TerraSynapse V2.1 Enterprise - Frontend Aprimorado
# Sistema #1 do mercado agro com IA avançada e UX premium
# Performance otimizada, alertas preditivos e análises agrônomas profissionais

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
from PIL import Image
import base64
from io import BytesIO

# ----------------------------------------------------------------------
# Configuração Enterprise
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="TerraSynapse Enterprise - Plataforma Líder em AgTech",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------- BRAND PREMIUM ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

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
  --ts-gradient: linear-gradient(135deg, rgba(0, 211, 149, 0.1), rgba(30, 64, 175, 0.1));
}

/* Reset e Base */
* { box-sizing: border-box; }
html, body, [class*="css"] { 
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
  color: var(--ts-text-primary);
  background: var(--ts-bg-dark);
}

/* Scrollbars customizadas */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--ts-bg-dark); }
::-webkit-scrollbar-thumb { background: var(--ts-primary); border-radius: 3px; }

/* Container principal */
.main .block-container { padding-top: 2rem; max-width: 1400px; }

/* Header Enterprise */
.ts-header {
  background: var(--ts-gradient);
  backdrop-filter: blur(20px);
  border: 1px solid var(--ts-border);
  border-radius: 16px;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.ts-header::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: var(--ts-gradient);
  opacity: 0.1;
  z-index: -1;
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

/* Navegação Premium */
.ts-nav {
  display: flex;
  gap: 0.5rem;
  margin: 1.5rem 0;
  overflow-x: auto;
  padding: 0.5rem;
  background: var(--ts-bg-card);
  border-radius: 12px;
  border: 1px solid var(--ts-border);
}

.ts-nav-item {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  background: transparent;
  color: var(--ts-text-secondary);
  border: 1px solid transparent;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  white-space: nowrap;
}

.ts-nav-item:hover {
  background: rgba(0, 211, 149, 0.1);
  color: var(--ts-primary);
  border-color: rgba(0, 211, 149, 0.3);
}

.ts-nav-item.active {
  background: var(--ts-primary);
  color: var(--ts-bg-dark);
  font-weight: 600;
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

/* Grid responsivo */
.ts-grid {
  display: grid;
  gap: 1.5rem;
  margin: 1.5rem 0;
}

.ts-grid-2 { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
.ts-grid-3 { grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
.ts-grid-4 { grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); }

/* Botões Premium */
.ts-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
  text-decoration: none;
}

.ts-btn-primary {
  background: var(--ts-primary);
  color: var(--ts-bg-dark);
}

.ts-btn-primary:hover {
  background: var(--ts-primary-dark);
  transform: translateY(-1px);
}

.ts-btn-secondary {
  background: var(--ts-bg-card);
  color: var(--ts-text-primary);
  border: 1px solid var(--ts-border);
}

.ts-btn-secondary:hover {
  border-color: var(--ts-primary);
  color: var(--ts-primary);
}

/* Gráficos customizados */
.ts-chart {
  background: var(--ts-bg-card);
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid var(--ts-border);
}

/* Tabelas */
.ts-table {
  width: 100%;
  background: var(--ts-bg-card);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--ts-border);
}

.ts-table th,
.ts-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--ts-border);
}

.ts-table th {
  background: rgba(0, 211, 149, 0.1);
  font-weight: 600;
  color: var(--ts-primary);
}

/* Loading states */
.ts-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--ts-text-secondary);
}

.ts-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--ts-border);
  border-top: 2px solid var(--ts-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 0.5rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Footer */
.ts-footer {
  margin-top: 3rem;
  padding: 2rem;
  border-top: 1px solid var(--ts-border);
  text-align: center;
  color: var(--ts-text-muted);
}

/* Responsividade */
@media (max-width: 768px) {
  .ts-header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .ts-nav {
    flex-direction: column;
  }
  
  .ts-kpi-value {
    font-size: 2rem;
  }
  
  .ts-grid-2,
  .ts-grid-3,
  .ts-grid-4 {
    grid-template-columns: 1fr;
  }
}

/* Animações */
.fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Hide Streamlit default elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }

/* Custom scrollbar for main content */
.main .block-container {
  scrollbar-width: thin;
  scrollbar-color: var(--ts-primary) var(--ts-bg-dark);
}
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

@st.cache_data(ttl=300, show_spinner=False)  # 5 min cache para geolocalização
def get_location_by_ip():
    """Geolocalização otimizada com cache longo"""
    try:
        session = st.session_state.http_session
        r = session.get("https://ipapi.co/json/", timeout=8)
        if r.status_code == 200:
            data = r.json()
            return (
                float(data.get("latitude", -15.78)), 
                float(data.get("longitude", -47.93)),
                data.get("city", "Brasília"), 
                data.get("region", "DF")
            )
    except:
        pass
    
    # Fallback para Capinópolis, MG baseado no documento
    return -18.6800, -49.5660, "Capinópolis", "MG"

@st.cache_data(ttl=3600, show_spinner=False)  # 1h cache para geocoding
def geocode_location(city: str, state: str):
    """Geocoding com cache longo"""
    api_key = st.secrets.get("openweather", {}).get("API_KEY", "")
    if not api_key:
        return None
    
    try:
        session = st.session_state.http_session
        url = "https://api.openweathermap.org/geo/1.0/direct"
        params = {"q": f"{city},{state},BR", "limit": 1, "appid": api_key}
        r = session.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except:
        pass
    return None

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
    st.session_state.current_view = "dashboard"
if "location" not in st.session_state:
    lat, lon, city, state = get_location_by_ip()
    st.session_state.location = {
        "lat": lat, "lon": lon, "city": city, "state": state, "mode": "auto"
    }
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False
if "alerts_history" not in st.session_state:
    st.session_state.alerts_history = []
if "trend_data" not in st.session_state:
    st.session_state.trend_data = {"et0": [], "ndvi": [], "timestamps": []}

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
    
    # Ajustes para condições específicas
    if R < 13 and 80 <= T <= 112:
        HI -= ((13 - R)/4)*math.sqrt((17 - abs(T-95.))/17)
    if R > 85 and 80 <= T <= 87:
        HI += 0.02*(R-85)*(87-T)
    
    hi_c = (HI - 32) * 5/9
    
    # Classificação de risco
    if hi_c >= 54: risk = "Perigo Extremo"
    elif hi_c >= 41: risk = "Perigo"
    elif hi_c >= 32: risk = "Cuidado Extremo"
    elif hi_c >= 27: risk = "Cuidado"
    else: risk = "Conforto"
    
    return round(hi_c, 1), risk

def calculate_vpd(temp_c: float, humidity: float) -> tuple:
    """Calcula déficit de pressão de vapor"""
    # Pressão de vapor de saturação
    es = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    # Pressão de vapor atual
    ea = es * (humidity / 100)
    # VPD
    vpd = es - ea
    
    # Classificação para plantas
    if vpd > 3.0: status = "Estresse Severo"
    elif vpd > 2.0: status = "Estresse Alto"
    elif vpd > 1.2: status = "Estresse Moderado"
    elif vpd > 0.4: status = "Ideal"
    else: status = "Muito Baixo"
    
    return round(vpd, 2), status

def calculate_gdd(temp_max: float, temp_min: float, base_temp: float = 10) -> float:
    """Calcula graus-dia de crescimento"""
    avg_temp = (temp_max + temp_min) / 2
    gdd = max(0, avg_temp - base_temp)
    return round(gdd, 1)

def predict_disease_risk(temp: float, humidity: float, rain: float) -> dict:
    """IA para predição de risco de doenças"""
    risks = {}
    
    # Ferrugem (alta umidade + temperatura moderada)
    if humidity > 80 and 20 <= temp <= 30:
        risks["Ferrugem"] = "Alto"
    elif humidity > 60 and 15 <= temp <= 35:
        risks["Ferrugem"] = "Médio"
    else:
        risks["Ferrugem"] = "Baixo"
    
    # Fusarium (alta umidade + temperatura alta)
    if humidity > 75 and temp > 28:
        risks["Fusarium"] = "Alto"
    elif humidity > 60 and temp > 25:
        risks["Fusarium"] = "Médio"
    else:
        risks["Fusarium"] = "Baixo"
    
    # Antracnose (chuva + temperatura alta)
    if rain > 10 and temp > 25:
        risks["Antracnose"] = "Alto"
    elif rain > 5 and temp > 20:
        risks["Antracnose"] = "Médio"
    else:
        risks["Antracnose"] = "Baixo"
    
    return risks

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
    
    # Alertas informativos
    if 4 < et0 <= 6:
        alerts.append({
            "level": "info",
            "title": "Demanda Hídrica Moderada",
            "message": f"ET0 de {et0} mm/dia indica necessidade de irrigação moderada.",
            "action": "Monitorar umidade do solo. Programar irrigação se necessário."
        })
    
    return alerts

# ----------------------------------------------------------------------
# Header Enterprise
# ----------------------------------------------------------------------
def render_header():
    # Status da API
    health_code, health_data = cached_api_request("GET", "/health")
    api_status = "ONLINE" if health_code == 200 else "OFFLINE"
    status_color = "var(--ts-success)" if health_code == 200 else "var(--ts-danger)"
    
    st.markdown(f"""
    <div class="ts-header fade-in">
        <div class="ts-header-content">
            <div class="ts-logo">
                🌾 TerraSynapse Enterprise
            </div>
            <div class="ts-status">
                <div class="ts-badge">
                    <div class="ts-indicator" style="background: {status_color};"></div>
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
# Navegação Premium
# ----------------------------------------------------------------------
def render_navigation():
    views = [
        ("dashboard", "📊 Dashboard", "Visão geral executiva"),
        ("climate", "🌤️ Clima IA", "Análise meteorológica avançada"), 
        ("vegetation", "🛰️ NDVI Pro", "Monitoramento por satélite"),
        ("market", "📈 Mercado", "Preços em tempo real"),
        ("profitability", "💰 Rentabilidade", "Análise financeira"),
        ("alerts", "⚠️ Alertas", "Centro de notificações")
    ]
    
    nav_html = '<div class="ts-nav">'
    for view_id, label, description in views:
        active_class = "active" if st.session_state.current_view == view_id else ""
        nav_html += f'''
        <div class="ts-nav-item {active_class}" 
             onclick="window.parent.location.search='?view={view_id}'"
             title="{description}">
            {label}
        </div>
        '''
    nav_html += '</div>'
    
    st.markdown(nav_html, unsafe_allow_html=True)
    
    # Processar mudança de view via query params
    try:
        params = st.query_params
        if "view" in params:
            new_view = params["view"]
            if new_view != st.session_state.current_view:
                st.session_state.current_view = new_view
                st.rerun()
    except:
        pass

# ----------------------------------------------------------------------
# Sidebar Premium
# ----------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("### 🔐 Portal Executivo")
        
        if not st.session_state.logged_in:
            # Login/Cadastro Premium
            st.markdown("""
            <div class="ts-card">
                <h4>Bem-vindo ao TerraSynapse</h4>
                <p>Plataforma líder em inteligência agrícola com IA avançada.</p>
            </div>
            """, unsafe_allow_html=True)
            
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
                        st.session_state.user_data = {"nome": "Demo User", "empresa": "TerraSynapse"}
                        st.success("Modo demo ativado!")
                        st.rerun()
            
            with tab2:
                with st.form("register_form"):
                    nome = st.text_input("👤 Nome Completo")
                    email_reg = st.text_input("📧 Email Corporativo")
                    password_reg = st.text_input("🔒 Senha", type="password")
                    empresa = st.text_input("🏢 Empresa/Propriedade")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        cidade = st.text_input("🌍 Cidade", value=st.session_state.location["city"])
                    with col2:
                        estados = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT",
                                  "PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
                        estado = st.selectbox("📍 Estado", estados, 
                                            index=estados.index(st.session_state.location["state"]) 
                                            if st.session_state.location["state"] in estados else 12)
                    
                    perfil = st.selectbox("🎯 Perfil", 
                                        ["Produtor Rural", "Agrônomo", "Técnico Agrícola", "Consultor",
                                         "Cooperativa", "Gerente Agrícola", "Investidor", "Outro"])
                    
                    if st.form_submit_button("🌾 Criar Conta Enterprise", type="primary", use_container_width=True):
                        if nome and email_reg and password_reg:
                            payload = {
                                "nome_completo": nome, "email": email_reg, "password": password_reg,
                                "empresa_propriedade": empresa, "cidade": cidade, "estado": estado,
                                "perfil_profissional": perfil
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
            
            st.markdown(f"""
            <div class="ts-card">
                <h4>👋 Bem-vindo, {user_name}!</h4>
                <p>Acesso Enterprise ativo</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Configurações de localização
            with st.expander("📍 Configuração de Local", expanded=False):
                location_mode = st.radio("Modo de localização:", 
                                        ["Automática (IP)", "Cidade/Estado", "Coordenadas"])
                
                if location_mode == "Automática (IP)":
                    if st.button("🔄 Detectar automaticamente", use_container_width=True):
                        lat, lon, city, state = get_location_by_ip()
                        st.session_state.location.update({
                            "lat": lat, "lon": lon, "city": city, "state": state, "mode": "auto"
                        })
                        st.success(f"Local atualizado: {city}, {state}")
                        st.rerun()
                
                elif location_mode == "Cidade/Estado":
                    col1, col2 = st.columns(2)
                    with col1:
                        city_input = st.text_input("Cidade", value=st.session_state.location["city"])
                    with col2:
                        estados = ["AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS","MT",
                                  "PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"]
                        state_input = st.selectbox("Estado", estados,
                                                  index=estados.index(st.session_state.location["state"]) 
                                                  if st.session_state.location["state"] in estados else 12)
                    
                    if st.button("📡 Geocodificar", use_container_width=True):
                        coords = geocode_location(city_input, state_input)
                        if coords:
                            lat, lon = coords
                            st.session_state.location.update({
                                "lat": lat, "lon": lon, "city": city_input, "state": state_input, "mode": "geo"
                            })
                            st.success(f"Coordenadas encontradas: {lat:.4f}, {lon:.4f}")
                            st.rerun()
                        else:
                            st.error("Não foi possível geocodificar. Verifique a API key do OpenWeather.")
                
                else:  # Coordenadas
                    col1, col2 = st.columns(2)
                    with col1:
                        lat_input = st.number_input("Latitude", value=st.session_state.location["lat"], 
                                                   format="%.6f", step=0.000001)
                    with col2:
                        lon_input = st.number_input("Longitude", value=st.session_state.location["lon"], 
                                                   format="%.6f", step=0.000001)
                    
                    if st.button("✅ Aplicar coordenadas", use_container_width=True):
                        st.session_state.location.update({
                            "lat": lat_input, "lon": lon_input, "mode": "manual"
                        })
                        st.success("Coordenadas aplicadas!")
                        st.rerun()
            
            # Configurações avançadas
            with st.expander("⚙️ Configurações Avançadas", expanded=False):
                st.session_state.auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", 
                                                           value=st.session_state.auto_refresh)
                
                if st.button("🗑️ Limpar cache", use_container_width=True):
                    st.cache_data.clear()
                    st.success("Cache limpo!")
                
                # Diagnóstico do sistema
                st.markdown("**Diagnóstico do Sistema:**")
                health_code, health_data = cached_api_request("GET", "/health")
                if health_code == 200:
                    st.success("✅ API Online")
                    if isinstance(health_data, dict):
                        st.json(health_data)
                else:
                    st.error("❌ API Offline")
            
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
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**📍 Local:** {st.session_state.location['city']}, {st.session_state.location['state']} "
                   f"({lat:.4f}, {lon:.4f})")
    with col2:
        if st.button("🔄 Atualizar", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col3:
        if st.session_state.auto_refresh:
            st.caption("Auto-refresh ativo")
            time.sleep(30)
            st.cache_data.clear()
            st.rerun()
    
    # Obter dados do dashboard
    token = st.session_state.user_token if st.session_state.user_token != "demo_token" else None
    code, dashboard_data = cached_api_request("GET", f"/dashboard/{lat}/{lon}", token=token)
    
    if code == 200 and isinstance(dashboard_data, dict) and dashboard_data.get("status") == "success":
        data = dashboard_data["data"]
        climate = data["clima"]
        vegetation = data["vegetacao"] 
        market = data["mercado"]
        profitability = data["rentabilidade"]
        
        # KPIs principais
        st.markdown("### 📊 Indicadores Principais")
        kpi_cols = st.columns(4)
        
        with kpi_cols[0]:
            st.markdown(f"""
            <div class="ts-card ts-kpi">
                <div class="ts-kpi-value">{climate['temperatura']}°C</div>
                <div class="ts-kpi-label">Temperatura</div>
                <div class="ts-kpi-delta positive">Umidade: {climate['umidade']}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with kpi_cols[1]:
            et0_status = "Alta" if climate['et0'] > 6 else "Normal" if climate['et0'] > 3 else "Baixa"
            delta_class = "negative" if climate['et0'] > 6 else "positive"
            st.markdown(f"""
            <div class="ts-card ts-kpi">
                <div class="ts-kpi-value">{climate['et0']}</div>
                <div class="ts-kpi-label">ET0 (mm/dia)</div>
                <div class="ts-kpi-delta {delta_class}">{et0_status}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with kpi_cols[2]:
            ndvi_status = "Excelente" if vegetation['ndvi'] > 0.7 else "Bom" if vegetation['ndvi'] > 0.5 else "Atenção"
            delta_class = "positive" if vegetation['ndvi'] > 0.5 else "negative"
            st.markdown(f"""
            <div class="ts-card ts-kpi">
                <div class="ts-kpi-value">{vegetation['ndvi']}</div>
                <div class="ts-kpi-label">NDVI</div>
                <div class="ts-kpi-delta {delta_class}">{ndvi_status}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with kpi_cols[3]:
            receita = profitability['receita_por_hectare']
            st.markdown(f"""
            <div class="ts-card ts-kpi">
                <div class="ts-kpi-value">R$ {receita:,.0f}</div>
                <div class="ts-kpi-label">Receita/ha</div>
                <div class="ts-kpi-delta positive">{profitability['produtividade_estimada']} sc/ha</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Sistema de alertas inteligentes
        st.markdown("### ⚠️ Centro de Alertas Inteligentes")
        alerts = generate_smart_alerts(climate, vegetation)
        
        if alerts:
            for alert in alerts:
                level = alert["level"]
                if level == "critical":
                    alert_class = "critical"
                elif level == "warning":
                    alert_class = "warning"
                else:
                    alert_class = "info"
                
                st.markdown(f"""
                <div class="ts-alert {alert_class}">
                    <strong>{alert['title']}</strong><br>
                    {alert['message']}<br>
                    <small><strong>Ação recomendada:</strong> {alert['action']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="ts-alert success">
                <strong>✅ Sistema Operacional</strong><br>
                Nenhum alerta crítico detectado. Condições favoráveis para as operações agrícolas.
            </div>
            """, unsafe_allow_html=True)
        
        # Análises avançadas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌡️ Análise Térmica")
            temp = float(climate['temperatura'])
            humidity = float(climate['umidade'])
            
            heat_index, hi_risk = calculate_heat_index(temp, humidity)
            vpd, vpd_status = calculate_vpd(temp, humidity)
            
            st.markdown(f"""
            <div class="ts-card">
                <p><strong>Índice de Calor:</strong> {heat_index}°C ({hi_risk})</p>
                <p><strong>Déficit Pressão Vapor:</strong> {vpd} kPa ({vpd_status})</p>
                <p><strong>Recomendação:</strong> {climate['recomendacao_irrigacao']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 🦠 Risco de Doenças")
            disease_risks = predict_disease_risk(temp, humidity, 0)  # rain=0 por enquanto
            
            risk_html = "<div class='ts-card'>"
            for disease, risk_level in disease_risks.items():
                color = "var(--ts-danger)" if risk_level == "Alto" else "var(--ts-warning)" if risk_level == "Médio" else "var(--ts-success)"
                risk_html += f"<p><strong>{disease}:</strong> <span style='color: {color}'>{risk_level}</span></p>"
            risk_html += "</div>"
            
            st.markdown(risk_html, unsafe_allow_html=True)
    
    else:
        # Modo demo com dados simulados
        st.markdown("### 📊 Dashboard (Modo Demo)")
        st.info("Conecte-se ao backend para dados reais em tempo real")
        
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
        metrics = [
            (col1, "🌡️ Temperatura", f"{climate['temperatura']}°C"),
            (col2, "💧 Umidade", f"{climate['umidade']}%"),
            (col3, "💨 Vento", f"{climate['vento']} km/h"),
            (col4, "📊 Pressão", f"{climate['pressao']} hPa"),
            (col5, "☁️ Condição", climate['descricao'])
        ]
        
        for col, label, value in metrics:
            with col:
                st.markdown(f"""
                <div class="ts-card" style="text-align: center;">
                    <h4 style="margin: 0; color: var(--ts-primary);">{label}</h4>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 600;">{value}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Análises agrônomas avançadas
        temp = float(climate['temperatura'])
        humidity = float(climate['umidade'])
        
        heat_index, hi_risk = calculate_heat_index(temp, humidity)
        vpd, vpd_status = calculate_vpd(temp, humidity)
        
        st.markdown("### 🧬 Índices Agronômicos Avançados")
        
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
                    'bar': {'color': "var(--ts-primary)"},
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
            # Gauge para VPD
            fig_vpd = go.Figure(go.Indicator(
                mode="gauge+number",
                value=vpd,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"VPD - {vpd_status}"},
                gauge={
                    'axis': {'range': [None, 4]},
                    'bar': {'color': "var(--ts-secondary)"},
                    'steps': [
                        {'range': [0, 0.4], 'color': "#EF4444"},
                        {'range': [0.4, 1.2], 'color': "#10B981"},
                        {'range': [1.2, 2.0], 'color': "#F59E0B"},
                        {'range': [2.0, 4], 'color': "#EF4444"}
                    ]
                }
            ))
            fig_vpd.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20),
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_vpd, use_container_width=True)
        
        with col3:
            # Gauge para ET0
            fig_et0 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=climate['et0'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Evapotranspiração"},
                gauge={
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "var(--ts-info)"},
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
        
        # Recomendações inteligentes
        st.markdown("### 🎯 Recomendações Agronômicas")
        st.markdown(f"""
        <div class="ts-card">
            <h4>💧 Irrigação:</h4>
            <p>{climate['recomendacao_irrigacao']}</p>
            
            <h4>🌡️ Manejo Térmico:</h4>
            <p>Com heat index de {heat_index}°C ({hi_risk}), 
            {'considere medidas de proteção para trabalhadores' if heat_index > 32 else 'condições confortáveis para atividades'}.</p>
            
            <h4>🌱 Estresse Hídrico:</h4>
            <p>VPD de {vpd} kPa indica {vpd_status.lower()}. 
            {'Monitore sinais de estresse nas plantas' if vpd > 2.0 else 'Condições favoráveis para desenvolvimento vegetal'}.</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.info("Conecte-se ao backend para análises climáticas em tempo real")

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
            st.markdown(f"""
            <div class="ts-card ts-kpi">
                <div class="ts-kpi-value">{vegetation['ndvi']}</div>
                <div class="ts-kpi-label">Índice NDVI</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="ts-card ts-kpi">
                <div class="ts-kpi-value">{vegetation['status_vegetacao']}</div>
                <div class="ts-kpi-label">Status</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="ts-card ts-kpi">
                <div class="ts-kpi-value">{vegetation['data_analise']}</div>
                <div class="ts-kpi-label">Última Análise</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Interpretação NDVI
        ndvi_value = float(vegetation['ndvi'])
        if ndvi_value > 0.7:
            interpretation = "Vegetação densa e saudável"
            color = "var(--ts-success)"
        elif ndvi_value > 0.5:
            interpretation = "Vegetação moderada"
            color = "var(--ts-warning)"
        elif ndvi_value > 0.3:
            interpretation = "Vegetação esparsa"
            color = "var(--ts-warning)"
        else:
            interpretation = "Solo exposto ou vegetação estressada"
            color = "var(--ts-danger)"
        
        st.markdown(f"""
        <div class="ts-card">
            <h4>📊 Interpretação do NDVI</h4>
            <p style="color: {color}; font-weight: 600;">{interpretation}</p>
            <p><strong>Recomendação:</strong> {vegetation['recomendacao']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Histórico simulado (em produção viria do backend)
        st.markdown("### 📈 Tendência NDVI (Últimos 30 dias)")
        
        # Gerar dados simulados para demonstração
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base_ndvi = float(vegetation['ndvi'])
        ndvi_values = [base_ndvi + np.random.normal(0, 0.05) for _ in range(30)]
        
        fig = px.line(x=dates, y=ndvi_values, title="Evolução do NDVI")
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="NDVI",
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_traces(line_color="var(--ts-primary)")
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("Conecte-se ao backend para dados de satélite em tempo real")

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
        commodities = [
            (col1, "🌱 Soja", market["soja"]["preco"], market["soja"].get("variacao", 0)),
            (col2, "🌽 Milho", market["milho"]["preco"], market["milho"].get("variacao", 0)),
            (col3, "☕ Café", market["cafe"]["preco"], market["cafe"].get("variacao", 0))
        ]
        
        for col, name, price, variation in commodities:
            with col:
                delta_class = "positive" if variation >= 0 else "negative"
                delta_text = f"↑ {variation:.1f}%" if variation >= 0 else f"↓ {abs(variation):.1f}%"
                
                st.markdown(f"""
                <div class="ts-card ts-kpi">
                    <div class="ts-kpi-value">R$ {price:.2f}</div>
                    <div class="ts-kpi-label">{name}</div>
                    <div class="ts-kpi-delta {delta_class}">{delta_text}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Gráfico de preços
        commodities_data = {
            'Commodity': ['Soja', 'Milho', 'Café'],
            'Preço': [market["soja"]["preco"], market["milho"]["preco"], market["cafe"]["preco"]]
        }
        
        df_market = pd.DataFrame(commodities_data)
        fig = px.bar(df_market, x='Commodity', y='Preço', 
                    title="Preços Atuais das Commodities",
                    color='Preço',
                    color_continuous_scale='Viridis')
        fig.update_layout(
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Análise de tendências
        st.markdown("### 📊 Análise de Mercado")
        st.markdown("""
        <div class="ts-card">
            <h4>💡 Insights de Mercado</h4>
            <p>• <strong>Soja:</strong> Preços estáveis com demanda forte do mercado externo</p>
            <p>• <strong>Milho:</strong> Pressão de alta devido à safrinha menor</p>
            <p>• <strong>Café:</strong> Volatilidade devido às condições climáticas</p>
            <br>
            <p><strong>Recomendação:</strong> Momento favorável para comercialização de soja. 
            Considere estratégias de hedge para milho e café.</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.info("Conecte-se ao backend para dados de mercado em tempo real")

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
        st.markdown(f"""
        <div class="ts-card ts-kpi">
            <div class="ts-kpi-value">R$ {receita_total:,.0f}</div>
            <div class="ts-kpi-label">Receita Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with result_cols[1]:
        st.markdown(f"""
        <div class="ts-card ts-kpi">
            <div class="ts-kpi-value">R$ {custo_total:,.0f}</div>
            <div class="ts-kpi-label">Custo Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with result_cols[2]:
        color = "positive" if lucro_bruto > 0 else "negative"
        st.markdown(f"""
        <div class="ts-card ts-kpi">
            <div class="ts-kpi-value">R$ {lucro_bruto:,.0f}</div>
            <div class="ts-kpi-label">Lucro Bruto</div>
            <div class="ts-kpi-delta {color}">
                {"Lucro" if lucro_bruto > 0 else "Prejuízo"}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with result_cols[3]:
        st.markdown(f"""
        <div class="ts-card ts-kpi">
            <div class="ts-kpi-value">{margem:.1f}%</div>
            <div class="ts-kpi-label">Margem</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Análise de sensibilidade
    st.markdown("### 🎯 Análise de Sensibilidade")
    
    # Gráfico de breakeven
    preco_range = np.arange(preco_saca * 0.7, preco_saca * 1.3, preco_saca * 0.05)
    lucros = []
    
    for preco in preco_range:
        receita = area * produtividade * preco
        lucro = receita - custo_total
        lucros.append(lucro)
    
    fig_sensitivity = px.line(x=preco_range, y=lucros, 
                             title="Análise de Sensibilidade - Preço vs Lucro")
    fig_sensitivity.add_hline(y=0, line_dash="dash", line_color="red", 
                             annotation_text="Ponto de Equilíbrio")
    fig_sensitivity.update_layout(
        xaxis_title="Preço/saca (R$)",
        yaxis_title="Lucro Total (R$)",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_sensitivity, use_container_width=True)
    
    # Recomendações
    ponto_equilibrio = custo_total / (area * produtividade)
    
    st.markdown(f"""
    <div class="ts-card">
        <h4>💡 Análise Financeira</h4>
        <p><strong>Ponto de Equilíbrio:</strong> R$ {ponto_equilibrio:.2f}/saca</p>
        <p><strong>ROI Projetado:</strong> {(lucro_bruto/custo_total*100):.1f}% sobre investimento</p>
        <p><strong>Receita por hectare:</strong> R$ {(receita_total/area):,.0f}</p>
        <p><strong>Custo por hectare:</strong> R$ {(custo_total/area):,.0f}</p>
        
        <h4>🎯 Recomendações:</h4>
        {"<p style='color: var(--ts-success)'>✅ Projeto viável com margem positiva</p>" if margem > 0 else "<p style='color: var(--ts-danger)'>⚠️ Revisar custos ou aguardar melhor momento de mercado</p>"}
        {"<p>• Considere contratos futuros para garantir preço atual</p>" if margem > 15 else ""}
        {"<p>• Avalie oportunidades de redução de custos</p>" if margem < 20 else ""}
    </div>
    """, unsafe_allow_html=True)

def render_alerts():
    """Centro de alertas e notificações"""
    st.markdown("### ⚠️ Centro de Alertas Inteligentes")
    
    # Configurações de alertas
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🔔 Configurações de Notificação")
        
        alert_settings = {
            "temp_max": st.slider("Temperatura máxima (°C)", 25, 45, 35),
            "humidity_min": st.slider("Umidade mínima (%)", 10, 50, 30),
            "wind_max": st.slider("Vento máximo (km/h)", 10, 50, 25),
            "et0_max": st.slider("ET0 máximo (mm/dia)", 3, 10, 6),
            "ndvi_min": st.slider("NDVI mínimo", 0.1, 0.8, 0.5)
        }
    
    with col2:
        st.markdown("#### 📱 Canais de Notificação")
        email_alerts = st.checkbox("Email", value=True)
        sms_alerts = st.checkbox("SMS", value=False)
        push_alerts = st.checkbox("Push Notifications", value=True)
        whatsapp_alerts = st.checkbox("WhatsApp", value=False)
    
    # Histórico de alertas (simulado)
    st.markdown("### 📋 Histórico de Alertas")
    
    alert_history = [
        {"time": "2024-01-15 14:30", "level": "critical", "title": "Risco de Incêndio", "status": "Ativo"},
        {"time": "2024-01-15 10:15", "level": "warning", "title": "ET0 Elevada", "status": "Resolvido"},
        {"time": "2024-01-14 16:45", "level": "info", "title": "Chuva Prevista", "status": "Resolvido"},
        {"time": "2024-01-14 08:20", "level": "warning", "title": "Vento Forte", "status": "Resolvido"},
        {"time": "2024-01-13 12:00", "level": "critical", "title": "NDVI Baixo", "status": "Em Análise"}
    ]
    
    for alert in alert_history:
        level_colors = {
            "critical": "var(--ts-danger)",
            "warning": "var(--ts-warning)", 
            "info": "var(--ts-info)"
        }
        
        status_colors = {
            "Ativo": "var(--ts-danger)",
            "Resolvido": "var(--ts-success)",
            "Em Análise": "var(--ts-warning)"
        }
        
        st.markdown(f"""
        <div class="ts-card" style="border-left: 4px solid {level_colors[alert['level']]};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4 style="margin: 0; color: {level_colors[alert['level']]};">{alert['title']}</h4>
                    <p style="margin: 0.5rem 0 0 0; color: var(--ts-text-secondary);">{alert['time']}</p>
                </div>
                <div style="padding: 0.25rem 0.75rem; background: rgba(255,255,255,0.1); 
                           border-radius: 12px; color: {status_colors[alert['status']]}; font-weight: 600;">
                    {alert['status']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Aplicação Principal
# ----------------------------------------------------------------------
def main():
    """Aplicação principal"""
    
    # Renderizar componentes
    render_header()
    
    if st.session_state.logged_in:
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
        st.markdown("""
        <div class="ts-card" style="text-align: center; padding: 3rem 2rem;">
            <h1>🌾 TerraSynapse Enterprise</h1>
            <h3>Plataforma #1 em Inteligência Agrícola</h3>
            <p style="font-size: 1.2rem; margin: 2rem 0;">
                Transforme sua operação agrícola com IA avançada, 
                monitoramento por satélite e análises preditivas.
            </p>
            
            <div class="ts-grid ts-grid-3" style="margin: 3rem 0;">
                <div class="ts-card">
                    <h4>🌤️ Clima Inteligente</h4>
                    <p>Previsões precisas com alertas preditivos para tomada de decisão assertiva</p>
                </div>
                <div class="ts-card">
                    <h4>🛰️ NDVI por Satélite</h4>
                    <p>Monitoramento da vegetação em tempo real com análises agronômicas avançadas</p>
                </div>
                <div class="ts-card">
                    <h4>📈 Mercado em Tempo Real</h4>
                    <p>Preços atualizados e análises de tendências para maximizar rentabilidade</p>
                </div>
            </div>
            
            <p style="color: var(--ts-text-secondary);">
                Faça login na barra lateral para acessar todas as funcionalidades
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar sempre visível
    render_sidebar()
    
    # Footer
    st.markdown("""
    <div class="ts-footer">
        <p>© 2024 TerraSynapse Enterprise - Liderando a Revolução AgTech</p>
        <p>
            📧 <a href="mailto:terrasynapse@terrasynapse.com">terrasynapse@terrasynapse.com</a> • 
            📱 (34) 99972-9740 • 
            🌐 Capinópolis, MG
        </p>
    </div>
    """, unsafe_allow_html=True)

# Executar aplicação
if __name__ == "__main__":
    main()
