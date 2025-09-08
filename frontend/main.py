import streamlit as st
import requests
import json
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="TerraSynapse - Plataforma Agrícola Enterprise",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URLs das APIs
BACKEND_URL = "https://terrasynapse-backend.onrender.com"

def fazer_requisicao(endpoint, method="GET", data=None, token=None):
    """Função para fazer requisições à API"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=15)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na API: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        st.warning("Tempo limite excedido - API inicializando")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão: {str(e)}")
        return None

def obter_localizacao():
    """Obter localização via IP"""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=8)
        if response.status_code == 200:
            data = response.json()
            return data["lat"], data["lon"], data["city"], data["region"]
    except:
        pass
    
    return -15.7942, -47.8822, "Brasília", "DF"

# Inicialização do estado da sessão
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_token" not in st.session_state:
    st.session_state.user_token = None
if "user_data" not in st.session_state:
    st.session_state.user_data = None

# Header TerraSynapse
st.title("🌾 TerraSynapse V2.0")
st.subheader("Plataforma Enterprise de Monitoramento Agrícola")
st.divider()

# Sidebar
with st.sidebar:
    st.header("🔐 Portal Executivo")
    
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["🔑 Login", "👤 Cadastro"])
        
        with tab1:
            st.subheader("Acesso Executivo")
            
            email = st.text_input("📧 Email Corporativo", key="login_email")
            password = st.text_input("🔒 Senha", type="password", key="login_password")
            
            if st.button("🚀 Entrar", type="primary", use_container_width=True):
                if email and password:
                    with st.spinner("🔄 Autenticando..."):
                        result = fazer_requisicao("/login", "POST", {
                            "email": email,
                            "password": password
                        })
                        
                        if result and "access_token" in result:
                            st.session_state.logged_in = True
                            st.session_state.user_token = result["access_token"]
                            st.session_state.user_data = result["user"]
                            st.success("✅ Login realizado com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Credenciais inválidas")
                else:
                    st.warning("⚠️ Preencha todos os campos")
        
        with tab2:
            st.subheader("Registro Enterprise")
            
            nome = st.text_input("👤 Nome Completo", key="reg_nome")
            email_reg = st.text_input("📧 Email", key="reg_email")
            password_reg = st.text_input("🔒 Senha", type="password", key="reg_password")
            
            perfil = st.selectbox("🎯 Perfil Profissional", [
                "Produtor Rural", "Agrônomo", "Técnico Agrícola", 
                "Consultor", "Cooperativa", "Gerente Agrícola", "Outro"
            ])
            
            empresa = st.text_input("🏢 Empresa", key="reg_empresa")
            cidade = st.text_input("🌍 Cidade", key="reg_cidade")
            
            estado = st.selectbox("📍 Estado", [
                "SP", "MG", "MT", "GO", "MS", "PR", "RS", "SC",
                "BA", "TO", "MA", "PI", "CE", "RN", "PB", "PE",
                "AL", "SE", "ES", "RJ", "AC", "RO", "AM", "RR", 
                "PA", "AP", "DF"
            ])
            
            if st.button("🎯 Criar Conta Enterprise", type="primary", use_container_width=True):
                if nome and email_reg and password_reg:
                    with st.spinner("🔄 Criando conta..."):
                        result = fazer_requisicao("/register", "POST", {
                            "nome_completo": nome,
                            "email": email_reg,
                            "password": password_reg,
                            "perfil_profissional": perfil,
                            "empresa_propriedade": empresa,
                            "cidade": cidade,
                            "estado": estado
                        })
                        
                        if result and "access_token" in result:
                            st.session_state.logged_in = True
                            st.session_state.user_token = result["access_token"]
                            st.session_state.user_data = result["user"]
                            st.success("✅ Conta criada com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Erro no cadastro")
                else:
                    st.warning("⚠️ Preencha todos os campos obrigatórios")
    
    else:
        st.success(f"👋 Bem-vindo, {st.session_state.user_data['nome']}!")
        st.info("🟢 Sistema Online")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_token = None
            st.session_state.user_data = None
            st.rerun()

# Conteúdo principal
if st.session_state.logged_in:
    # Obter localização
    lat, lon, cidade, estado = obter_localizacao()
    
    st.info(f"📍 Localização: {cidade}, {estado} • {lat:.4f}, {lon:.4f}")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 Atualizar Dados", type="primary"):
            st.rerun()
    
    with col2:
        auto_refresh = st.checkbox("⚡ Auto-refresh (30s)")
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    st.divider()
    
    # Buscar dados do dashboard
    with st.spinner("🔄 Carregando inteligência agrícola..."):
        dashboard_data = fazer_requisicao(
            f"/dashboard/{lat}/{lon}", 
            token=st.session_state.user_token
        )
    
    if dashboard_data and dashboard_data.get("status") == "success":
        data = dashboard_data["data"]
        
        # Métricas principais
        st.header("📊 Dashboard Executivo - Tempo Real")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🌡️ Temperatura", 
                f"{data['clima']['temperatura']}°C",
                delta=f"Umidade: {data['clima']['umidade']}%"
            )
        
        with col2:
            et0_delta = "Crítico" if data['clima']['et0'] > 6 else "Normal"
            st.metric(
                "💧 ET0", 
                f"{data['clima']['et0']} mm/dia",
                delta=et0_delta
            )
        
        with col3:
            st.metric(
                "🌱 NDVI", 
                f"{data['vegetacao']['ndvi']}",
                delta=data['vegetacao']['status_vegetacao']
            )
        
        with col4:
            receita = data['rentabilidade']['receita_por_hectare']
            st.metric(
                "💰 Receita/ha", 
                f"R$ {receita:,.0f}",
                delta=f"{data['rentabilidade']['produtividade_estimada']} sc/ha"
            )
        
        st.divider()
        
        # Sistema de Alertas
        st.header("⚠️ Centro de Alertas Inteligentes")
        
        if data["alertas"]:
            for alerta in data["alertas"]:
                if alerta["prioridade"] == "alta":
                    st.error(f"🚨 ALERTA CRÍTICO: {alerta['mensagem']}")
                else:
                    st.warning(f"⚠️ ATENÇÃO: {alerta['mensagem']}")
        else:
            st.success("✅ SISTEMA OPERACIONAL: Nenhum alerta crítico detectado.")
        
        st.divider()
        
        # Gráficos
        st.header("📈 Análise Técnica Avançada")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌡️ Evapotranspiração (ET0)")
            
            # Gráfico ET0
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = data['clima']['et0'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "ET0 (mm/dia)"},
                delta = {'reference': 5},
                gauge = {
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "#2E7D32"},
                    'steps': [
                        {'range': [0, 3], 'color': "lightgray"},
                        {'range': [3, 6], 'color': "yellow"},
                        {'range': [6, 10], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 6
                    }
                }
            ))
            
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            st.subheader("📈 Preços de Commodities")
            
            # Gráfico de commodities
            commodities = data["mercado"]
            df_precos = pd.DataFrame([
                {"Commodity": "Soja", "Preço": commodities["soja"]["preco"]},
                {"Commodity": "Milho", "Preço": commodities["milho"]["preco"]},
                {"Commodity": "Café", "Preço": commodities["cafe"]["preco"]}
            ])
            
            fig_bar = px.bar(
                df_precos, 
                x="Commodity", 
                y="Preço",
                title="Preços Atuais (R$/saca)",
                color="Preço",
                color_continuous_scale="Greens"
            )
            
            fig_bar.update_layout(height=300)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.divider()
        
        # Análise Detalhada
        st.header("🔬 Análise Técnica Executiva")
        
        tab1, tab2, tab3 = st.tabs(["🌡️ Climatologia", "🌱 Vegetação", "💰 Mercado"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Condições Meteorológicas")
                st.write(f"**Temperatura:** {data['clima']['temperatura']}°C")
                st.write(f"**Umidade:** {data['clima']['umidade']}%")
                st.write(f"**Vento:** {data['clima']['vento']} km/h")
                st.write(f"**Pressão:** {data['clima']['pressao']} hPa")
                st.write(f"**Condição:** {data['clima']['descricao']}")
            
            with col2:
                st.subheader("💧 Gestão de Irrigação")
                st.write(f"**ET0:** {data['clima']['et0']} mm/dia")
                st.write(f"**Recomendação:** {data['clima']['recomendacao_irrigacao']}")
                
                if data['clima']['et0'] > 6:
                    st.error("🚨 ET0 elevada - Irrigação urgente recomendada")
                elif data['clima']['et0'] > 4:
                    st.warning("⚠️ ET0 moderada - Monitorar necessidade de irrigação")
                else:
                    st.success("✅ ET0 baixa - Irrigação não necessária")
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🛰️ Análise NDVI")
                st.write(f"**Valor:** {data['vegetacao']['ndvi']}")
                st.write(f"**Status:** {data['vegetacao']['status_vegetacao']}")
                st.write(f"**Data:** {data['vegetacao']['data_analise']}")
            
            with col2:
                st.subheader("📋 Recomendações Técnicas")
                st.info(data['vegetacao']['recomendacao'])
                
                ndvi_val = data['vegetacao']['ndvi']
                if ndvi_val > 0.7:
                    st.success("🌟 Vegetação saudável e vigorosa")
                elif ndvi_val > 0.5:
                    st.info("📈 Vegetação em desenvolvimento normal")
                elif ndvi_val > 0.3:
                    st.warning("📉 Vegetação com estresse moderado")
                else:
                    st.error("🚨 Vegetação em estado crítico")
        
        with tab3:
            st.subheader("📈 Análise de Mercado")
            
            for commodity, info in data['mercado'].items():
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        f"{commodity.title()}",
                        f"R$ {info['preco']}/saca"
                    )
                
                with col2:
                    st.metric(
                        "Variação",
                        f"{info['variacao']:+.2f}%"
                    )
                
                with col3:
                    if commodity == "soja":
                        receita_estimada = info['preco'] * data['rentabilidade']['produtividade_estimada']
                        st.metric(
                            "Receita/ha",
                            f"R$ {receita_estimada:,.0f}"
                        )
        
        st.divider()
        
        # Calculadora de Rentabilidade
        st.header("🧮 Calculadora Enterprise de Rentabilidade")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            area_ha = st.number_input("🌾 Área (hectares)", min_value=1, value=10, step=1)
        
        with col2:
            cultura_select = st.selectbox("🌱 Cultura Principal", ["Soja", "Milho", "Café"])
        
        with col3:
            produtividade = st.number_input("📊 Produtividade (sacas/ha)", min_value=1, value=50, step=1)
        
        if cultura_select.lower() in data['mercado']:
            preco_cultura = data['mercado'][cultura_select.lower()]['preco']
            receita_total = area_ha * produtividade * preco_cultura
            
            # Custos estimados
            custo_por_ha = 3000
            custo_total = area_ha * custo_por_ha
            lucro_total = receita_total - custo_total
            margem = (lucro_total / receita_total) * 100 if receita_total > 0 else 0
            
            st.subheader(f"💰 Projeção Financeira - {cultura_select}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Receita Total", f"R$ {receita_total:,.0f}")
            
            with col2:
                st.metric("Custo Estimado", f"R$ {custo_total:,.0f}")
            
            with col3:
                st.metric("Lucro Projetado", f"R$ {lucro_total:,.0f}")
            
            st.write(f"**Área:** {area_ha} ha | **Produtividade:** {produtividade} sc/ha | **Preço:** R$ {preco_cultura}/saca | **Margem:** {margem:.1f}%")
            
            if receita_total > 200000:
                st.success("🎯 Excelente potencial de receita! Propriedade altamente rentável.")
            elif receita_total > 100000:
                st.info("📊 Boa projeção de receita. Considere otimizações para maximizar lucros.")
            else:
                st.warning("💡 Receita moderada. Analise possibilidades de aumento de produtividade.")
        
        # Footer
        st.divider()
        st.write(f"**TerraSynapse V2.0** - Plataforma Enterprise | Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | 🟢 Sistema Online")
    
    else:
        st.error("❌ Erro ao carregar dados do dashboard")
        st.info("🔄 Tentando reconectar com a API...")

else:
    # Página inicial
    st.header("🌾 TerraSynapse V2.0 Enterprise")
    st.subheader("Plataforma Líder em Inteligência Agrícola")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🌡️ Monitoramento Climático**")
        st.write("Dados meteorológicos em tempo real com cálculo preciso de evapotranspiração e recomendações inteligentes de irrigação.")
        
        st.write("**🛰️ Análise por Satélite**")
        st.write("Índices NDVI avançados para monitoramento da saúde vegetal com alertas automáticos de estresse.")
    
    with col2:
        st.write("**💰 Inteligência de Mercado**")
        st.write("Preços atualizados de commodities com análise de tendências e calculadora de rentabilidade.")
        
        st.write("**📊 Dashboard Executivo**")
        st.write("Visão completa da propriedade com alertas inteligentes e relatórios automatizados.")
    
    st.info("🚀 Faça login ou cadastre-se na barra lateral para acessar dados personalizados da sua propriedade.")
    
    # Demonstração
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🌡️ Temperatura", "24.5°C", "Ideal para cultivo")
    
    with col2:
        st.metric("🌱 NDVI", "0.75", "Vegetação saudável")
    
    with col3:
        st.metric("💰 Soja", "R$ 165.50/sc", "+2.3%")

# Diagnóstico do Sistema
if st.sidebar.button("🔧 Diagnóstico do Sistema", use_container_width=True):
    with st.spinner("🔄 Executando diagnóstico..."):
        health = fazer_requisicao("/health")
        if health:
            st.sidebar.success("✅ APIs TerraSynapse Online")
            st.sidebar.json(health)
        else:
            st.sidebar.error("❌ Sistema Temporariamente Indisponível")
