import streamlit as st
import requests

class AuthSystem:
    def __init__(self, backend_url="https://terrasynapse-backend.onrender.com"):
        self.backend_url = backend_url
        self.init_session_state()
    
    def init_session_state(self):
        """Inicializar estado da sessão de forma robusta"""
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'access_token' not in st.session_state:
            st.session_state.access_token = None
        if 'dashboard_config' not in st.session_state:
            st.session_state.dashboard_config = None
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'dashboard'
            
    def is_authenticated(self):
        """Verificar se usuário está autenticado com verificação segura"""
        return (hasattr(st.session_state, 'user') and 
                st.session_state.user is not None and 
                hasattr(st.session_state, 'access_token') and
                st.session_state.access_token is not None)

    def render_auth_page(self):
        st.title("TerraSynapse - Sistema Profissional")
        
        tab1, tab2 = st.tabs(["Login", "Cadastro"])
        
        with tab1:
            self.render_login_form()
        
        with tab2:
            self.render_register_form()

    def render_login_form(self):
        st.subheader("Login Profissional")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Senha", type="password")
            
            if st.form_submit_button("Entrar"):
                if email and password:
                    st.session_state.user = {
                        "nome_completo": "Usuário Profissional",
                        "email": email,
                        "perfil_profissional": "agronomo",
                        "empresa_propriedade": "Fazenda Tecnológica",
                        "cidade": "São Paulo",
                        "estado": "SP"
                    }
                    st.rerun()

    def render_register_form(self):
        st.subheader("Cadastro Profissional")
        
        profiles = [
            "Engenheiro Agrônomo",
            "Zootecnista", 
            "Pecuarista de Corte",
            "Pecuarista Leiteiro",
            "Especialista em Genética",
            "Proprietário de Haras",
            "Gestor do Agronegócio"
        ]
        
        with st.form("register_form"):
            nome = st.text_input("Nome Completo")
            email = st.text_input("Email Profissional")
            password = st.text_input("Senha", type="password")
            perfil = st.selectbox("Perfil Profissional", profiles)
            empresa = st.text_input("Empresa/Propriedade")
            cidade = st.text_input("Cidade")
            estado = st.selectbox("Estado", ["SP", "MG", "GO", "MT", "RS", "PR", "SC"])
            
            if st.form_submit_button("Cadastrar"):
                if all([nome, email, password, empresa, cidade]):
                    st.session_state.user = {
                        "nome_completo": nome,
                        "email": email,
                        "perfil_profissional": perfil.lower().replace(" ", "_"),
                        "empresa_propriedade": empresa,
                        "cidade": cidade,
                        "estado": estado
                    }
                    st.success("Cadastro realizado com sucesso!")
                    st.rerun()

    def logout(self):
        st.session_state.user = None
        st.session_state.access_token = None
        st.rerun()

auth_system = AuthSystem()
