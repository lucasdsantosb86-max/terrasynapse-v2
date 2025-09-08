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
        if 'registered_users' not in st.session_state:
            st.session_state.registered_users = {}

    def is_authenticated(self):
        return st.session_state.user is not None

    def render_auth_page(self):
        st.title("TerraSynapse - Sistema Profissional")
        
        tab1, tab2 = st.tabs(["Login", "Cadastro"])
        
        with tab1:
            self.render_login_form()
        
        with tab2:
            self.render_register_form()

    def render_login_form(self):
        st.subheader("Login")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Senha", type="password")
            
            if st.form_submit_button("Entrar"):
                if email and password:
                    # Verificar se usuário está registrado
                    if email in st.session_state.registered_users:
                        user_data = st.session_state.registered_users[email]
                        if user_data['password'] == password:
                            st.session_state.user = user_data.copy()
                            del st.session_state.user['password']  # Remover senha da sessão
                            st.success(f"Bem-vindo, {user_data['nome_completo']}!")
                            st.rerun()
                        else:
                            st.error("Senha incorreta")
                    else:
                        st.error("Email não encontrado. Faça seu cadastro primeiro.")

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
            estado = st.selectbox("Estado", ["SP", "MG", "GO", "MT", "RS", "PR", "SC", "BA", "MS"])
            
            if st.form_submit_button("Cadastrar"):
                if all([nome, email, password, empresa, cidade]):
                    if email not in st.session_state.registered_users:
                        user_data = {
                            "nome_completo": nome,
                            "email": email,
                            "password": password,
                            "perfil_profissional": perfil.lower().replace(" ", "_"),
                            "empresa_propriedade": empresa,
                            "cidade": cidade,
                            "estado": estado
                        }
                        st.session_state.registered_users[email] = user_data
                        st.success("Cadastro realizado com sucesso! Agora faça login.")
                    else:
                        st.error("Email já cadastrado")
                else:
                    st.error("Preencha todos os campos")

    def logout(self):
        st.session_state.user = None
        st.rerun()

auth_system = AuthSystem()
