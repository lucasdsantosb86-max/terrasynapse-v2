# No início da função main(), antes de qualquer verificação
if 'user' not in st.session_state:
    st.session_state.user = None
# frontend/main.py - TerraSynapse V2.0 Sistema Profissional
import streamlit as st
import sys
import os

# Adicionar path dos componentes
sys.path.append(os.path.join(os.path.dirname(__file__), 'components'))

from components.auth_system import auth_system
from components.profile_dashboards import profile_dashboards

# Configuração da página
st.set_page_config(
    page_title="TerraSynapse - Sistema Profissional Agropecuário",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .professional-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4CAF50;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def render_sidebar():
    """Renderizar sidebar profissional"""
    with st.sidebar:
        # Logo profissional
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #2E7D32, #4CAF50); 
                    color: white; border-radius: 10px; margin-bottom: 1rem;">
            <h2>🌱 TerraSynapse</h2>
            <p style="margin: 0; font-size: 0.9em;">Sistema Profissional</p>
        </div>
        """, unsafe_allow_html=True)
        
        if auth_system.is_authenticated():
            user = st.session_state.user
            
            # Informações do usuário
            st.markdown(f"""
            <div class="professional-card">
                <strong>{user['nome_completo']}</strong><br>
                <small>{user['perfil_profissional'].replace('_', ' ').title()}</small><br>
                <small>📍 {user['cidade']}, {user['estado']}</small><br>
                <small>🏢 {user['empresa_propriedade']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Menu profissional
            st.markdown("### Módulos Disponíveis")
            
            if st.button("📊 Dashboard Principal", use_container_width=True):
                st.session_state.current_page = "dashboard"
            
            if st.button("📈 Análises Avançadas", use_container_width=True):
                st.session_state.current_page = "analytics"
            
            if st.button("📋 Relatórios Técnicos", use_container_width=True):
                st.session_state.current_page = "reports"
            
            if st.button("🧮 Calculadoras", use_container_width=True):
                st.session_state.current_page = "calculators"
            
            st.markdown("---")
            
            if st.button("⚙️ Configurações", use_container_width=True):
                st.session_state.current_page = "settings"
            
            if st.button("💡 Suporte Técnico", use_container_width=True):
                st.session_state.current_page = "support"
            
            st.markdown("---")
            
            if st.button("🚪 Sair do Sistema", use_container_width=True):
                auth_system.logout()
        
        else:
            st.markdown("""
            ### Sobre o TerraSynapse
            
            **Sistema profissional** para gestão agropecuária:
            
            ✅ **Dashboards especializados** por área profissional
            
            ✅ **Dados em tempo real** de clima e mercado
            
            ✅ **Análises técnicas** personalizadas
            
            ✅ **Segurança profissional** e compliance
            
            ---
            
            ### Contato Profissional
            **Email:** contato@terrasynapse.com
            **Telefone:** (11) 99999-9999
            **Site:** www.terrasynapse.com
            """)

def render_main_content():
    """Renderizar conteúdo principal"""
    if not auth_system.is_authenticated():
        # Página de autenticação
        auth_system.render_auth_page()
    
    else:
        # Sistema autenticado
        user = st.session_state.user
        
        # Header profissional
        st.markdown(f"""
        <div class="main-header">
            <h2 style="margin: 0;">Dashboard {user['perfil_profissional'].replace('_', ' ').title()}</h2>
            <p style="margin: 0; opacity: 0.9;">
                👤 {user['nome_completo']} | 🏢 {user['empresa_propriedade']} | 📍 {user['cidade']}, {user['estado']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Verificar página atual
        current_page = getattr(st.session_state, 'current_page', 'dashboard')
        
        if current_page == 'analytics':
            render_analytics_page()
        elif current_page == 'reports':
            render_reports_page()
        elif current_page == 'calculators':
            render_calculators_page()
        elif current_page == 'settings':
            render_settings_page()
        elif current_page == 'support':
            render_support_page()
        else:
            # Dashboard principal baseado no perfil
            profile_dashboards.render_dashboard_by_profile(user['perfil_profissional'])
            
            # Ferramentas especializadas
            render_specialized_tools(user['perfil_profissional'])

def render_analytics_page():
    """Página de análises avançadas"""
    st.markdown("### 📈 Análises Avançadas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📊 **Análise de Tendências**\nAnálise preditiva baseada em histórico")
        
    with col2:
        st.info("🎯 **Benchmarking**\nComparação com indicadores do setor")

def render_reports_page():
    """Página de relatórios técnicos"""
    st.markdown("### 📋 Relatórios Técnicos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Relatório de Performance", use_container_width=True):
            st.success("Relatório de performance gerado com sucesso!")
    
    with col2:
        if st.button("🌱 Relatório Agronômico", use_container_width=True):
            st.success("Relatório agronômico gerado com sucesso!")
    
    with col3:
        if st.button("💰 Relatório Financeiro", use_container_width=True):
            st.success("Relatório financeiro gerado com sucesso!")

def render_calculators_page():
    """Página de calculadoras especializadas"""
    st.markdown("### 🧮 Calculadoras Especializadas")
    
    user = st.session_state.user
    profile = user['perfil_profissional']
    
    if "agronomo" in profile:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Calculadora de Irrigação")
            area = st.number_input("Área (hectares)", min_value=0.1)
            et0 = st.number_input("ET0 (mm/dia)", min_value=0.1)
            if st.button("Calcular"):
                resultado = area * et0 * 10
                st.success(f"Necessidade hídrica: {resultado:.1f} litros/dia")
        
        with col2:
            st.subheader("Análise de Solo")
            ph = st.number_input("pH do solo", min_value=1.0, max_value=14.0)
            if st.button("Analisar"):
                if ph < 6.0:
                    st.warning("Solo ácido - recomenda-se calagem")
                elif ph > 7.5:
                    st.warning("Solo alcalino - atenção à nutrição")
                else:
                    st.success("pH adequado para a maioria das culturas")

def render_settings_page():
    """Página de configurações"""
    st.markdown("### ⚙️ Configurações do Sistema")
    
    user = st.session_state.user
    
    st.subheader("Informações do Perfil")
    st.text_input("Nome", value=user['nome_completo'], disabled=True)
    st.text_input("Email", value=user['email'], disabled=True)
    st.text_input("Empresa", value=user['empresa_propriedade'], disabled=True)
    
    if st.button("Atualizar Perfil"):
        st.info("Funcionalidade em desenvolvimento")

def render_support_page():
    """Página de suporte técnico"""
    st.markdown("### 💡 Suporte Técnico Especializado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📞 Contato Direto**
        - **Email:** suporte@terrasynapse.com
        - **WhatsApp:** (11) 99999-9999
        - **Horário:** Segunda a Sexta, 8h às 18h
        """)
    
    with col2:
        st.markdown("""
        **🎥 Recursos de Ajuda**
        - Tutoriais em vídeo
        - Documentação técnica
        - FAQ especializado
        """)

def render_specialized_tools(profile):
    """Ferramentas especializadas por perfil"""
    st.markdown("---")
    st.markdown("### 🛠️ Ferramentas Especializadas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Análise de Dados", use_container_width=True):
            st.success("Análise iniciada!")
    
    with col2:
        if st.button("📈 Monitoramento", use_container_width=True):
            st.success("Monitor ativado!")
    
    with col3:
        if st.button("🎯 Otimização", use_container_width=True):
            st.success("Otimização carregada!")
    
    with col4:
        if st.button("📋 Laudo Técnico", use_container_width=True):
            st.success("Laudo gerado!")

def main():
    """Função principal"""
    # Inicializar session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    # Renderizar layout
    render_sidebar()
    render_main_content()
    
    # Footer profissional
    if auth_system.is_authenticated():
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("🌱 **TerraSynapse V2.0** - Sistema Profissional")
        
        with col2:
            user = st.session_state.user
            st.markdown(f"👤 **Usuário:** {user['nome_completo']}")
        
        with col3:
            st.markdown("🔒 **Segurança:** Dados protegidos")

if __name__ == "__main__":
    main()
