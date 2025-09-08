<<<<<<< HEAD
﻿import streamlit as st
=======
# frontend/components/auth_system.py
import streamlit as st
>>>>>>> 4297b2e67cebe8edce4a28dae0ba6a8d48a56735
import requests
import json

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
        return st.session_state.access_token is not None

    def login(self, email: str, password: str) -> bool:
        try:
            response = requests.post(
                f"{self.backend_url}/auth/login",
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.access_token = data["access_token"]
                st.session_state.user = data["user"]
                return True
            return False
        except:
            return False

    def register(self, user_data: dict) -> bool:
        try:
            response = requests.post(
                f"{self.backend_url}/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            return response.status_code == 200
        except:
            return False

    def render_auth_page(self):
        st.title("TerraSynapse - Sistema Profissional")
        
        tab1, tab2 = st.tabs(["Login", "Cadastro"])
        
<<<<<<< HEAD
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
<<<<<<< HEAD
                        "cidade": "Cidade", 
=======
                        "cidade": "Cidade",
>>>>>>> ab0c6f6238c229159c6e680311316d12674c1883
                        "estado": "Estado"
=======
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", value="terrasynapse@terrasynapse.com")
                password = st.text_input("Senha", type="password", value="Luc084as688")
                
                if st.form_submit_button("Entrar"):
                    if self.login(email, password):
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas")
        
        with tab2:
            with st.form("register_form"):
                nome = st.text_input("Nome Completo")
                email = st.text_input("Email")
                password = st.text_input("Senha", type="password")
                perfil = st.selectbox("Perfil", ["engenheiro_agronomo", "zootecnista", "gestor_agronegocio"])
                empresa = st.text_input("Empresa")
                cidade = st.text_input("Cidade")
                estado = st.text_input("Estado")
                
                if st.form_submit_button("Cadastrar"):
                    user_data = {
                        "nome_completo": nome,
                        "email": email,
                        "password": password,
                        "perfil_profissional": perfil,
                        "empresa_propriedade": empresa,
                        "cidade": cidade,
                        "estado": estado
>>>>>>> 4297b2e67cebe8edce4a28dae0ba6a8d48a56735
                    }
                    if self.register(user_data):
                        st.success("Cadastro realizado! Faça login.")
                    else:
                        st.error("Erro no cadastro")

    def logout(self):
        st.session_state.user = None
        st.session_state.access_token = None
        st.rerun()

auth_system = AuthSystem()
