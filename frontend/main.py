# frontend/auth_main.py - TerraSynapse V2.0 com Autenticação
import streamlit as st
import sys
import os

# Adicionar path dos componentes
sys.path.append(os.path.join(os.path.dirname(__file__), 'components'))

from components.auth_system import auth_system
from components.profile_dashboards import profile_dashboards

# Configuração da página
st.set_page_config(
    page_title="TerraSynapse - Inteligência Agropecuária",
    page_icon="🌱",
    layout="wide"
)

def main():
    # Verificar autenticação
    if not auth_system.is_authenticated():
        auth_system.render_auth_page()
    else:
        user = st.session_state.user
        config = st.session_state.dashboard_config
        
        # Header
        st.markdown(f"# {config.get('titulo', 'Dashboard TerraSynapse')}")
        st.markdown(f"**👤 {user['nome_completo']}** | **🏢 {user['empresa_propriedade']}**")
        
        # Sidebar
        with st.sidebar:
            st.markdown(f"### Perfil: {user['perfil_profissional'].title()}")
            if st.button("🚪 Sair"):
                auth_system.logout()
        
        # Dashboard por perfil
        profile_dashboards.render_dashboard_by_profile(user['perfil_profissional'])

if __name__ == "__main__":
    main()
