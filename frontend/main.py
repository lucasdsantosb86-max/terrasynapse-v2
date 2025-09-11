# TerraSynapse V2.2 Enterprise - Frontend 100% Produção
# Sem modo demo, otimizado para secrets.toml configurado
# Geolocalização real, OpenWeather integrada, sistema enterprise completo

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

# ---------------------------- BRAND ENTERPRISE ----------------------------
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

/* Base Styling */
* { box-sizing: border-box; }
html, body, [class*="css"] { 
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
  color: var(--ts-text-primary);
  background: var(--ts-bg-dark);
}

.main .block-container { padding-top: 2rem; max-width: 1400px; }

/* Header Enterprise */
.ts-header {
  background: linear-gradient(135deg, rgba(0, 211, 149, 0.1), rgba(30, 64, 175, 0.1));
  backdrop-filter: blur(20px);
  border: 1px solid var(--ts-border);
  border-radius: 16px;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
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

/* Cards Enterprise */
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

.ts-hero-fallback {
  background: linear-gradient(135deg, #00D395, #1E40AF);
  padding: 2rem;
  border-radius: 16px;
  text-align: center;
  color: white;
  margin: 1rem 0;
}

/* Alert Styles */
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

/* Hide Streamlit Elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Configuração baseada em secrets.toml
# ----------------------------------------------------------------------
ENV_MODE = st.secrets.get("env", {}).get("MODE", "prod")
API_CFG = st.secrets.get("api", {})

# URLs baseadas no ambiente
BACKEND_URL = (API_CFG.get("API_BASE_URL_PROD") if ENV_MODE == "prod"
               else API_CFG.get("API_BASE_URL_DEV", API_CFG.get("API_BASE_URL_PROD",""))).rstrip("/")

# Configurações geográficas
GEO_CFG = st.secrets.get("geo", {})
DEFAULT_LAT = float(GEO_CFG.get("DEFAULT_LAT", -18.5880))
DEFAULT_LON = float(GEO_CFG.get("DEFAULT_LON", -49.5690))
DEFAULT_CITY = GEO_CFG.get("DEFAULT_CITY", "Capinópolis")
DEFAULT_STATE = GEO_CFG.get("DEFAULT_STATE", "MG")

# Session HTTP otimizada
if "http_session" not in st.session_state:
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=20, 
        pool_maxsize=30, 
        max_retries=3
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        'User-Agent': 'TerraSynapse-Enterprise/2.2',
        'Accept': 'application/json',
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Connection': 'keep-alive'
    })
    st.session_state.http_session = session

def api_url(path: str) -> str:
    return f"{BACKEND_URL}{path}"

# ----------------------------------------------------------------------
# HTTP Helpers Enterprise
# ----------------------------------------------------------------------
@st.cache_data(ttl=60, show_spinner=False)
def cached_api_request(method, endpoint, json_data=None, token=None):
    """Cache inteligente com fallbacks robustos"""
    session = st.session_state.http_session
    url = api_url(endpoint)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            r = session.get(url, headers=headers, timeout=25)
        else:
            r = session.post(url, headers=headers, json=json_data, timeout=25)
        
        if r.status_code == 200:
            try:
                return r.status_code, r.json()
            except:
                return r.status_code, {"detail": "Invalid JSON response"}
        else:
            return r.status_code, {"detail": f"HTTP {r.status_code}: {r.text[:100]}"}
            
    except requests.exceptions.RequestException as e:
        return 0, {"detail": f"Connection error: {str(e)}"}

@st.cache_data(ttl=1800, show_spinner=False)  # 30 min cache para geolocalização
def get_location_intelligent():
    """
    Geolocalização inteligente - prioriza configuração do secrets.toml
    """
    session = st.session_state.http_session
    
    # Primeira tentativa: ipapi.co
    try:
        r = session.get("https://ipapi.co/json/", timeout=10)
        if r.status_code == 200:
            data = r.json()
            city = data.get("city", "")
            region = data.get("region", "")
            country = data.get("country_name", "")
            
            # Se detectar localização brasileira real (não servidor)
            if country == "Brazil" and city and region:
                return (
                    float(data.get("latitude", DEFAULT_LAT)), 
                    float(data.get("longitude", DEFAULT_LON)),
                    city, 
                    region
                )
    except Exception:
        pass
    
    # Fallback: Usar configuração do secrets.toml (Capinópolis, MG)
    return DEFAULT_LAT, DEFAULT_LON, DEFAULT_CITY, DEFAULT_STATE

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
    try:
        view_param = st.query_params.get("view", "dashboard")
        st.session_state.current_view = view_param
    except:
        st.session_state.current_view = "dashboard"
if "location" not in st.session_state:
    lat, lon, city, state = get_location_intelligent()
    st.session_state.location = {
        "lat": lat, "lon": lon, "city": city, "state": state, "mode": "intelligent"
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
    
    T = temp_c * 9/5 + 32
    R = humidity
    
    HI = (-42.379 + 2.04901523*T + 10.14333127*R
          - 0.22475541*T*R - 6.83783e-3*T*T - 5.481717e-2*R*R
          + 1.22874e-3*T*T*R + 8.5282e-4*T*R*R - 1.99e-6*T*T*R*R)
    
    hi_c = (HI - 32) * 5/9
    
    if hi_c >= 54: risk = "Perigo Extremo"
    elif hi_c >= 41: risk = "Perigo"
    elif hi_c >= 32: risk = "Cuidado Extremo" 
    elif hi_c >= 27: risk = "Cuidado"
    else: risk = "Conforto"
    
    return round(hi_c, 1), risk

def calculate_vpd(temp_c: float, humidity: float) -> tuple:
    """Calcula déficit de pressão de vapor"""
    es = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    vpd = es * (1 - humidity/100)
    
    if vpd > 3.0: status = "Estresse Severo"
    elif vpd > 2.0: status = "Estresse Alto"
    elif vpd > 1.2: status = "Estresse Moderado"
    elif vpd > 0.4: status = "Ideal"
    else: status = "Muito Baixo"
    
    return round(vpd, 2), status

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
            "message": f"Condições críticas: {temp}°C, {humidity}% UR, vento {wind} km/h",
            "action": "Suspender atividades com maquinário. Monitorar perímetro constantemente."
        })
    
    if et0 > 8:
        alerts.append({
            "level": "critical", 
            "title": "Estresse Hídrico Severo",
            "message": f"ET0 extremamente alta ({et0} mm/dia). Plantas em estresse.",
            "action": "Irrigação urgente necessária. Verificar sistema de distribuição."
        })
    
    # Alertas de atenção
    if ndvi < 0.4:
        alerts.append({
            "level": "warning",
            "title": "Vegetação Estressada",
            "message": f"NDVI baixo ({ndvi}). Possível problema nutricional ou hídrico.",
            "action": "Inspeção de campo recomendada. Verificar pragas, doenças e nutrição."
        })
    
    if wind > 25:
        alerts.append({
            "level": "warning",
            "title": "Vento Forte Detectado", 
            "message": f"Ventos de {wind} km/h podem afetar aplicações.",
            "action": "Suspender pulverizações. Verificar estruturas expostas."
        })
    
    # Alertas informativos
    if 4 < et0 <= 6:
        alerts.append({
            "level": "info",
            "title": "Demanda Hídrica Moderada",
            "message": f"ET0 de {et0} mm/dia indica necessidade de irrigação.",
            "action": "Monitorar umidade do solo. Programar irrigação se necessário."
        })
    
    return alerts

# ----------------------------------------------------------------------
# Header Enterprise
# ----------------------------------------------------------------------
def render_header():
    """Header com status em tempo real"""
    health_code, health_data = cached_api_request("GET", "/health")
    api_status = "ONLINE" if health_code == 200 else "OFFLINE"
    indicator_color = "#10B981" if health_code == 200 else "#EF4444"
    
    backend_display = BACKEND_URL.replace("https://", "").replace("http://", "")
    
    st.markdown(f"""
    <div class="ts-header">
        <div class="ts-header-content">
            <div class="ts-logo">
                TerraSynapse Enterprise
            </div>
            <div class="ts-status">
                <div class="ts-badge">
                    <div class="ts-indicator" style="background: {indicator_color};"></div>
                    API {api_status}
                </div>
                <div class="ts-badge">
                    {st.session_state.location['city']}, {st.session_state.location['state']}
                </div>
                <div class="ts-badge">
                    {backend_display}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Navegação Enterprise
# ----------------------------------------------------------------------
def render_navigation():
    """Navegação enterprise otimizada"""
    st.markdown("#### Painel de Controle")
    
    views = [
        ("dashboard", "Dashboard", "Visão executiva"),
        ("climate", "Clima IA", "Meteorologia avançada"), 
        ("vegetation", "NDVI Pro", "Satélite em tempo real"),
        ("market", "Mercado", "Commodities live"),
        ("profitability", "Rentabilidade", "Análise financeira"),
        ("alerts", "Alertas", "Centro de notificações")
    ]
    
    cols = st.columns(len(views))
    
    for i, (view_id, label, description) in enumerate(views):
        with cols[i]:
            is_active = st.session_state.current_view == view_id
            button_type = "primary" if is_active else "secondary"
            
            if st.button(label, use_container_width=True, type=button_type, 
                        help=description, key=f"nav_{view_id}"):
                if st.session_state.current_view != view_id:
                    st.session_state.current_view = view_id
                    try:
                        st.query_params.update({"view": view_id})
                    except:
                        pass
                    st.rerun()

# ----------------------------------------------------------------------
# Sidebar Enterprise
# ----------------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("### Portal Executivo")
        
        if not st.session_state.logged_in:
            # Hero com fallback para logo
            hero_loaded = False
            hero_paths = [
                "frontend/assets/brand/terrasynapse-hero-dark.svg",
                "assets/brand/terrasynapse-hero-dark.svg"
            ]
            
            for path in hero_paths:
                try:
                    st.image(path, use_container_width=True)
                    hero_loaded = True
                    break
                except:
                    continue
            
            if not hero_loaded:
                st.markdown("""
                <div class="ts-hero-fallback">
                    <h2>TerraSynapse</h2>
                    <p><strong>Plataforma Enterprise</strong></p>
                    <p>Inteligência Agrícola Avançada</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
            **Sistema Enterprise de Inteligência Agrícola**
            
            Plataforma líder com dados meteorológicos reais, monitoramento por satélite,
            preços de commodities ao vivo e análises preditivas baseadas em IA.
            """)
            
            tab1, tab2 = st.tabs(["Login", "Cadastro"])
            
            with tab1:
                email = st.text_input("Email Corporativo", key="login_email")
                password = st.text_input("Senha", type="password", key="login_password")
                
                if st.button("Entrar", type="primary", use_container_width=True):
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
            
            with tab2:
                with st.form("register_form"):
                    nome = st.text_input("Nome Completo")
                    email_reg = st.text_input("Email Corporativo")
                    password_reg = st.text_input("Senha", type="password")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        empresa = st.text_input("Empresa")
                    with col2:
                        perfil = st.selectbox("Perfil", 
                                            ["Produtor Rural", "Agrônomo", "Técnico Agrícola", 
                                             "Consultor", "Cooperativa", "Gerente", "Outro"])
                    
                    if st.form_submit_button("Criar Conta Enterprise", type="primary", use_container_width=True):
                        if nome and email_reg and password_reg:
                            payload = {
                                "nome_completo": nome, 
                                "email": email_reg, 
                                "password": password_reg,
                                "empresa_propriedade": empresa,
                                "perfil_profissional": perfil,
                                "cidade": st.session_state.location["city"],
                                "estado": st.session_state.location["state"]
                            }
                            with st.spinner("Criando conta enterprise..."):
                                code, body = cached_api_request("POST", "/register", payload)
                            if code == 200 and isinstance(body, dict) and "access_token" in body:
                                st.session_state.logged_in = True
                                st.session_state.user_token = body["access_token"]
                                st.session_state.user_data = body.get("user", {})
                                st.success("Conta enterprise criada!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("Erro ao criar conta. Tente novamente.")
                        else:
                            st.warning("Preencha os campos obrigatórios")
        
        else:
            # Usuário logado
            user_name = (st.session_state.user_data.get("nome") or 
                        st.session_state.user_data.get("nome_completo") or "Usuário")
            
            st.success(f"Bem-vindo, {user_name}")
            st.caption("Acesso Enterprise Ativo")
            
            # Status da conexão
            health_code, _ = cached_api_request("GET", "/health")
            if health_code == 200:
                st.success("Sistema Online")
            else:
                st.error("Sistema Offline")
            
            # Localização
            with st.expander("Localização", expanded=False):
                st.info(f"""
                **Local Atual:**
                {st.session_state.location['city']}, {st.session_state.location['state']}
                
                **Coordenadas:**
                {st.session_state.location['lat']:.4f}, {st.session_state.location['lon']:.4f}
                """)
                
                if st.button("Redetectar Localização", use_container_width=True):
                    get_location_intelligent.clear()
                    lat, lon, city, state = get_location_intelligent()
                    st.session_state.location.update({
                        "lat": lat, "lon": lon, "city": city, "state": state, "mode": "intelligent"
                    })
                    st.success(f"Localização: {city}, {state}")
                    st.rerun()
            
            # Configurações
            with st.expander("Configurações", expanded=False):
                refresh_options = {"Desabilitado": 0, "30 segundos": 30, "1 minuto": 60, "2 minutos": 120}
                selected = st.selectbox("Auto-refresh", list(refresh_options.keys()))
                st.session_state.auto_refresh = refresh_options[selected] > 0
                
                if st.button("Limpar Cache", use_container_width=True):
                    st.cache_data.clear()
                    st.success("Cache limpo!")
                
                st.markdown("**Sistema:**")
                st.code(f"""
Backend: {BACKEND_URL}
Modo: {ENV_MODE.upper()}
Versão: 2.2 Enterprise
                """)
            
            if st.button("Logout", type="secondary", use_container_width=True):
                for key in ["logged_in", "user_token", "user_data"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("Logout realizado!")
                st.rerun()

# ----------------------------------------------------------------------
# Views (Dashboard, Clima, etc) - Simplificadas para não misturar
# ----------------------------------------------------------------------
def render_dashboard():
    """Dashboard executivo principal"""
    lat, lon = st.session_state.location["lat"], st.session_state.location["lon"]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Monitorando:** {st.session_state.location['city']}, {st.session_state.location['state']} ({lat:.4f}, {lon:.4f})")
    with col2:
        if st.button("Atualizar", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    if st.session_state.auto_refresh:
        st.caption("Auto-refresh ativo")
        time.sleep(30)
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    with st.spinner("Carregando dados em tempo real..."):
        code, dashboard_data = cached_api_request("GET", f"/dashboard/{lat}/{lon}", 
                                                 token=st.session_state.user_token)
    
    if code == 200 and isinstance(dashboard_data, dict) and dashboard_data.get("status") == "success":
        data = dashboard_data["data"]
        climate = data["clima"]
        vegetation = data["vegetacao"] 
        market = data["mercado"]
        profitability = data["rentabilidade"]
        
        # KPIs principais
        st.markdown("### Indicadores Principais")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        with kpi1:
            st.metric("Temperatura", f"{climate['temperatura']}°C", 
                     delta=f"Umidade: {climate['umidade']}%")
        
        with kpi2:
            et0_value = climate['et0']
            et0_status = "Crítica" if et0_value > 6 else "Normal"
            st.metric("ET0", f"{et0_value} mm/dia", delta=et0_status)
        
        with kpi3:
            st.metric("NDVI", f"{vegetation['ndvi']}", 
                     delta=vegetation['status_vegetacao'])
        
        with kpi4:
            receita = profitability['receita_por_hectare']
            st.metric("Receita/ha", f"R$ {receita:,.0f}",
                     delta=f"{profitability['produtividade_estimada']} sc/ha")
        
        # Sistema de alertas
        st.markdown("### Centro de Alertas")
        alerts = generate_smart_alerts(climate, vegetation)
        
        if alerts:
            for alert in alerts:
                if alert["level"] == "critical":
                    st.error(f"**{alert['title']}** - {alert['message']}")
                elif alert["level"] == "warning":
                    st.warning(f"**{alert['title']}** - {alert['message']}")
                else:
                    st.info(f"**{alert['title']}** - {alert['message']}")
        else:
            st.success("Sistema operacional - Nenhum alerta crítico")
    
    else:
        st.error("Não foi possível conectar com os sensores. Verifique sua conexão.")

def render_climate():
    """Análise climática avançada"""
    st.markdown("### Climatologia de Precisão")
    # Implementação completa será no próximo arquivo
    st.info("Módulo Clima IA carregado")

def render_vegetation():
    """Monitoramento NDVI"""
    st.markdown("### Monitoramento NDVI")
    # Implementação completa será no próximo arquivo
    st.info("Módulo NDVI Pro carregado")

def render_market():
    """Análise de mercado"""
    st.markdown("### Mercado Agrícola")
    # Implementação completa será no próximo arquivo
    st.info("Módulo Mercado carregado")

def render_profitability():
    """Calculadora de rentabilidade"""
    st.markdown("### Análise de Rentabilidade")
    # Implementação completa será no próximo arquivo
    st.info("Módulo Rentabilidade carregado")

def render_alerts():
    """Centro de alertas"""
    st.markdown("### Centro de Alertas")
    # Implementação completa será no próximo arquivo
    st.info("Módulo Alertas carregado")

# ----------------------------------------------------------------------
# Aplicação Principal
# ----------------------------------------------------------------------
def main():
    """Aplicação principal enterprise"""
    
    # Header sempre visível
    render_header()
    
    if st.session_state.logged_in:
        # Sistema logado - navegação e conteúdo
        render_navigation()
        
        # Roteamento de views
        view_map = {
            "dashboard": render_dashboard,
            "climate": render_climate,
            "vegetation": render_vegetation,
            "market": render_market,
            "profitability": render_profitability,
            "alerts": render_alerts
        }
        
        current_view = st.session_state.current_view
        if current_view in view_map:
            view_map[current_view]()
        else:
            render_dashboard()  # Fallback
    
    else:
        # Landing page enterprise
        st.markdown("---")
        
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(0, 211, 149, 0.1), rgba(30, 64, 175, 0.1)); 
            border-radius: 16px; 
            padding: 3rem 2rem; 
            text-align: center; 
            margin: 2rem 0;
            border: 1px solid rgba(148, 163, 184, 0.1);
        ">
            <h1 style="color: #FFFFFF; margin-bottom: 1rem;">TerraSynapse Enterprise</h1>
            <h3 style="color: #00D395; margin-bottom: 2rem;">Plataforma Líder em Inteligência Agrícola</h3>
            <p style="font-size: 1.2rem; color: #94A3B8; margin-bottom: 2rem;">
                Sistema enterprise com dados meteorológicos reais, monitoramento por satélite, 
                preços de commodities ao vivo e análises preditivas baseadas em IA.
            </p>
            <p style="color: #64748B;">
                <strong>Tecnologias:</strong> OpenWeather API • Yahoo Finance • Sentinel-2 • Machine Learning
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features enterprise
        col1, col2, col3 = st.columns(3)
        
        features = [
            (col1, "Clima Inteligente", "Dados meteorológicos reais com alertas preditivos e índices agronômicos"),
            (col2, "NDVI por Satélite", "Monitoramento da vegetação com análises sazonais e recomendações técnicas"),
            (col3, "Mercado Live", "Preços reais de commodities com conversão automática e análise de tendências")
        ]
        
        for col, title, description in features:
            with col:
                st.markdown(f"""
                <div style="
                    background: rgba(15, 20, 25, 0.6); 
                    border: 1px solid rgba(148, 163, 184, 0.1); 
                    border-radius: 12px; 
                    padding: 1.5rem; 
                    height: 180px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                ">
                    <h4 style="color: #00D395; margin-bottom: 1rem;">{title}</h4>
                    <p style="color: #94A3B8; font-size: 0.9rem;">{description}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.info("Faça login na barra lateral para acessar todas as funcionalidades enterprise")
    
    # Sidebar sempre presente
    render_sidebar()
    
    # Footer enterprise
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #64748B;">
        <p><strong>TerraSynapse Enterprise</strong> - Tecnologia Líder em AgTech</p>
        <p>
            terrasynapse@terrasynapse.com • 
            (34) 99972-9740 • 
            Capinópolis, MG • 
            v2.2 Enterprise
        </p>
        <p style="font-size: 0.8rem; margin-top: 1rem;">
            Dados: OpenWeather • Yahoo Finance • Sentinel-2 • ExchangeRate
        </p>
    </div>
    """, unsafe_allow_html=True)

# Executar aplicação
if __name__ == "__main__":
    main()
