# frontend/auth_main.py - Nova versão com autenticação
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
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Função principal do aplicativo"""
    
    # Verificar se usuário está autenticado
    if not auth_system.is_authenticated():
        # Página de login/cadastro
        auth_system.render_auth_page()
    else:
        # Dashboard autenticado
        user = st.session_state.user
        config = st.session_state.dashboard_config
        
        # Header personalizado
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, {config.get('cor_tema', '#388E3C')}, #4CAF50); 
                    padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
            <h2 style="margin: 0;">{config.get('titulo', 'Dashboard')}</h2>
            <p style="margin: 0; opacity: 0.9;">
                👤 {user['nome_completo']} | 🏢 {user['empresa_propriedade']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar com logout
        with st.sidebar:
            st.markdown(f"### Bem-vindo, {user['nome_completo']}")
            st.markdown(f"**Perfil:** {user['perfil_profissional']}")
            st.markdown(f"**Empresa:** {user['empresa_propriedade']}")
            
            if st.button("🚪 Sair"):
                auth_system.logout()
        
        # Dashboard específico do perfil
        profile_dashboards.render_dashboard_by_profile(user['perfil_profissional'])
        
        # Ferramentas adicionais
        st.markdown("---")
        st.markdown("### 🛠️ Ferramentas Especializadas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Relatórios", use_container_width=True):
                st.success("Relatório gerado!")
        
        with col2:
            if st.button("🧮 Calculadoras", use_container_width=True):
                st.success("Calculadora carregada!")
        
        with col3:
            if st.button("📈 Análises", use_container_width=True):
                st.success("Análise iniciada!")

if __name__ == "__main__":
    main()
