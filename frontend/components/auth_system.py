import streamlit as st
import requests

class AuthSystem:
    def __init__(self, backend_url="https://terrasynapse-backend.onrender.com"):
        self.backend_url = backend_url
        self.init_session_state()

    def init_session_state(self):
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'access_token' not in st.session_state:
            st.session_state.access_token = None

    def is_authenticated(self):
        return st.session_state.user is not None

    def render_auth_page(self):
        st.title("TerraSynapse - Sistema Profissional")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Login")
            email = st.text_input("Email")
            password = st.text_input("Senha", type="password")
            
            if st.button("Entrar"):
                if email and password:
                    st.session_state.user = {
                        "nome_completo": email,
                        "perfil_profissional": "agronomo",
                        "empresa_propriedade": "Empresa",
                        "cidade": "Cidade", 
                        "estado": "Estado"
                    }
                    st.rerun()
        
        with col2:
            st.info("Sistema especializado para profissionais do agronegócio")

    def logout(self):
        st.session_state.user = None
        st.rerun()

auth_system = AuthSystem()
