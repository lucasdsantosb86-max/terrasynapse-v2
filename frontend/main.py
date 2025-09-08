# frontend/main.py - TerraSynapse V2.0 Sistema Profissional
import streamlit as st
import requests
import json
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Configuração da página ANTES de qualquer import
st.set_page_config(
    page_title="TerraSynapse - Sistema Profissional",
    page_icon="🌱",
    layout="wide"
)

# Inicialização SEGURA do session_state - PRIMEIRA PRIORIDADE
def safe_init_session_state():
    """Inicialização robusta e à prova de erros do session_state"""
    session_defaults = {
        'user': None,
        'access_token': None,
        'dashboard_config': None,
        'current_page': 'dashboard'
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# EXECUTAR INICIALIZAÇÃO IMEDIATAMENTE
safe_init_session_state()

# Imports dos componentes APÓS inicialização
sys.path.append(os.path.join(os.path.dirname(__file__), 'components'))

try:
    from components.profile_dashboards import profile_dashboards
except ImportError as e:
    st.error(f"Erro ao carregar componentes: {e}")
    st.stop()

def is_user_authenticated():
    """Verificação segura de autenticação"""
    return (st.session_state.get('user') is not None and 
            st.session_state.get('access_token') is not None)

def render_sidebar():
    """Sidebar com verificações defensivas"""
    with st.sidebar:
        st.markdown("## TerraSynapse")
        st.markdown("Sistema Profissional")
        
        if is_user_authenticated():
            user = st.session_state.user
            st.markdown(f"**{user.get('nome_completo', 'Usuário')}**")
            st.markdown(f"Perfil: {user.get('perfil_profissional', 'N/A')}")
            
            if st.button("Sair"):
                st.session_state.user = None
                st.session_state.access_token = None
                st.rerun()
        else:
            st.markdown("Sistema especializado para profissionais do agronegócio")
            st.markdown("**Contato:**")
            st.markdown("📞 (34) 99972-9740")
            st.markdown("📧 contato@terrasynapse.com")

def render_main_content():
    """Conteúdo principal com tratamento de erros"""
    try:
        if not is_user_authenticated():
            auth_system.render_auth_page()
        else:
            user = st.session_state.user
            st.markdown(f"# Dashboard {user.get('perfil_profissional', 'Profissional').title()}")
            st.markdown(f"Bem-vindo, **{user.get('nome_completo', 'Usuário')}**")
            
            # Dashboard baseado no perfil
            profile = user.get('perfil_profissional', 'geral')
            profile_dashboards.render_dashboard_by_profile(profile)
            
    except Exception as e:
        st.error("Erro no sistema. Recarregando...")
        st.session_state.clear()
        st.rerun()

def main():
    """Função principal com arquitetura robusta"""
    # Garantir inicialização (redundância intencional)
    safe_init_session_state()
    
    # Renderizar interface
    render_sidebar()
    render_main_content()
    
    # Footer profissional
    st.markdown("---")
    st.markdown("TerraSynapse V2.0 - Sistema Profissional | Dados protegidos")

if __name__ == "__main__":
    main()
