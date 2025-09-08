import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import random

class ProfileDashboards:
    def __init__(self):
        self.current_date = datetime.now()
    
    def render_dashboard_by_profile(self, profile):
        """Renderizar dashboard baseado no perfil do usuário"""
        
        if "agronomo" in profile.lower():
            self.render_agronomo_dashboard()
        elif "zootecnista" in profile.lower():
            self.render_zootecnista_dashboard()
        elif "corte" in profile.lower():
            self.render_pecuaria_corte_dashboard()
        elif "leiteiro" in profile.lower():
            self.render_pecuaria_leite_dashboard()
        elif "genetica" in profile.lower():
            self.render_genetica_dashboard()
        elif "haras" in profile.lower():
            self.render_haras_dashboard()
        else:
            self.render_gestor_dashboard()

    def render_agronomo_dashboard(self):
        """Dashboard para Engenheiros Agrônomos"""
        st.markdown("### 🌾 Dashboard Agronômico Profissional")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌡️ Temperatura", "24.5°C", delta="2.1°C vs ontem")
        with col2:
            st.metric("💧 Umidade Solo", "68%", delta="5% vs semana")
        with col3:
            st.metric("🌱 NDVI Médio", "0.78", delta="0.05 vs mês")
        with col4:
            st.metric("🐛 Alertas Fitossanitários", "2", delta="-1 vs ontem")
        
        # Gráfico NDVI
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Evolução NDVI - 30 dias")
            dates = pd.date_range(start=self.current_date - timedelta(days=30), 
                                end=self.current_date, freq='D')
            ndvi_values = [0.6 + 0.2 * random.random() for _ in dates]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=ndvi_values, 
                                   mode='lines+markers', name='NDVI',
                                   line=dict(color='#2E7D32', width=3)))
            fig.update_layout(title="Vigor Vegetativo", height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Precipitação vs Irrigação")
            days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
            precipitacao = [5, 0, 12, 8, 0, 15, 3]
            irrigacao = [10, 15, 5, 8, 12, 0, 10]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Precipitação', x=days, y=precipitacao))
            fig.add_trace(go.Bar(name='Irrigação', x=days, y=irrigacao))
            fig.update_layout(title="Suprimento Hídrico", height=300, barmode='stack')
            st.plotly_chart(fig, use_container_width=True)

    def render_zootecnista_dashboard(self):
        """Dashboard para Zootecnistas"""
        st.markdown("### 🐄 Dashboard Zootécnico Profissional")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🐄 Total Animais", "1,247", delta="12 nascimentos")
        with col2:
            st.metric("🌾 Capacidade Pastagem", "85%", delta="-5% vs mês")
        with col3:
            st.metric("💊 Taxa Reprodução", "78%", delta="3% vs ano")
        with col4:
            st.metric("⚕️ Em Tratamento", "23", delta="-5 vs semana")

    def render_pecuaria_corte_dashboard(self):
        """Dashboard para Pecuária de Corte"""
        st.markdown("### 🥩 Dashboard Pecuária de Corte")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Preço Arroba", "R$ 245,50", delta="R$ 8,50 vs semana")
        with col2:
            st.metric("⚖️ Peso Médio", "487 kg", delta="12 kg vs mês")
        with col3:
            st.metric("📊 GMD", "1.2 kg/dia", delta="0.1 kg vs período")
        with col4:
            st.metric("🎯 Prontos p/ Abate", "87", delta="23 vs mês")

    def render_pecuaria_leite_dashboard(self):
        """Dashboard para Pecuária Leiteira"""
        st.markdown("### 🥛 Dashboard Pecuária Leiteira")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🥛 Produção Diária", "2,847 L", delta="127 L vs ontem")
        with col2:
            st.metric("🐄 Vacas Lactação", "287", delta="5 novas")
        with col3:
            st.metric("📊 Média/Vaca", "24.8 L", delta="1.2 L vs mês")
        with col4:
            st.metric("🧪 CCS", "185 mil", delta="-15 mil")

    def render_genetica_dashboard(self):
        """Dashboard para Especialistas em Genética"""
        st.markdown("### 🧬 Dashboard Genética Animal")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👨‍👩‍👧‍👦 Genealogias", "1,847", delta="23 novas")
        with col2:
            st.metric("🎯 DEP Peso 450d", "+28.5", delta="+2.1")
        with col3:
            st.metric("💎 Acurácia", "87%", delta="3%")
        with col4:
            st.metric("🔄 Acasalamentos", "156", delta="42")

    def render_haras_dashboard(self):
        """Dashboard para Proprietários de Haras"""
        st.markdown("### 🐎 Dashboard Equinocultura")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🐎 Total Equinos", "247", delta="8 potros")
        with col2:
            st.metric("🤰 Éguas Gestantes", "47", delta="12 confirmações")
        with col3:
            st.metric("🏆 Em Treinamento", "23", delta="5 novos")
        with col4:
            st.metric("📊 Taxa Concepção", "78%", delta="5%")

    def render_gestor_dashboard(self):
        """Dashboard para Gestores do Agronegócio"""
        st.markdown("### 📊 Dashboard Gestão Agronegócio")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Receita Mensal", "R$ 485.7k", delta="12.3%")
        with col2:
            st.metric("📈 ROI", "18.5%", delta="2.1%")
        with col3:
            st.metric("⚡ Eficiência Op.", "92%", delta="5%")
        with col4:
            st.metric("🎯 Meta Cumprida", "95%", delta="8%")

profile_dashboards = ProfileDashboards()
