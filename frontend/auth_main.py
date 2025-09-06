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
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Função principal do aplicativo"""
    
    # CSS customizado
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(90deg, #2E7D32, #4CAF50);
            padding: 1rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
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
        <div class="main-header">
            <h2 style="margin: 0;">{config.get('titulo', 'Dashboard TerraSynapse')}</h2>
            <p style="margin: 0; opacity: 0.9;">
                👤 {user['nome_completo']} | 🏢 {user['empresa_propriedade']} | 📍 {user['cidade']}, {user['estado']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar com informações do usuário
        with st.sidebar:
            st.markdown(f"""
            ### 👤 Perfil Ativo
            **Nome:** {user['nome_completo']}  
            **Perfil:** {user['perfil_profissional'].replace('_', ' ').title()}  
            **Empresa:** {user['empresa_propriedade']}  
            **Localização:** {user['cidade']}, {user['estado']}
            """)
            
            st.markdown("---")
            
            if st.button("🚪 Sair do Sistema", use_container_width=True):
                auth_system.logout()
        
        # Dashboard específico do perfil
        profile_dashboards.render_dashboard_by_profile(user['perfil_profissional'])
        
        # Ferramentas especializadas
        st.markdown("---")
        st.markdown("### 🛠️ Ferramentas Especializadas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Relatórios Técnicos", use_container_width=True):
                st.success("✅ Relatório técnico gerado!")
        
        with col2:
            if st.button("🧮 Calculadoras Agro", use_container_width=True):
                st.success("✅ Calculadora carregada!")
        
        with col3:
            if st.button("📈 Análises Avançadas", use_container_width=True):
                st.success("✅ Análise iniciada!")
        
        with col4:
            if st.button("💡 Suporte Técnico", use_container_width=True):
                st.info("📞 Contato: suporte@terrasynapse.com")
        
        # Footer profissional
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("🌱 **TerraSynapse V2.0** - Sistema Profissional")
        
        with col2:
            st.markdown(f"⚡ **Status:** Sistema Online - Perfil {user['perfil_profissional'].title()}")
        
        with col3:
            st.markdown("🔒 **Segurança:** Dados protegidos LGPD")

if __name__ == "__main__":
    main()
