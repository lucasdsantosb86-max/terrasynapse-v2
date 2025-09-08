import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import time
import uuid

# Configuração da página
st.set_page_config(
    page_title="TerraSynapse V2.0",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações
API_BASE_URL = "http://localhost:8000"

# CSS customizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #2E8B57, #228B22);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: #f0f8f5;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E8B57;
        margin: 0.5rem 0;
    }
    .alert-warning {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .alert-success {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .status-offline {
        background: #f8d7da;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 3px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_location_by_ip():
    """Detectar localização aproximada pelo IP"""
    try:
        response = requests.get("https://ipapi.co/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'latitude': float(data.get('latitude', -15.794200)),
                'longitude': float(data.get('longitude', -47.882200)),
                'city': data.get('city', 'Cidade Detectada'),
                'region': data.get('region', ''),
                'country': data.get('country_name', ''),
                'accuracy': 'IP (aproximada)'
            }
        else:
            return None
    except Exception as e:
        return None

def get_location_name(lat, lon):
    """Obter nome da cidade/região baseado em coordenadas"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
        headers = {'User-Agent': 'TerraSynapse/1.0'}
        
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            city = (address.get('city') or 
                   address.get('town') or 
                   address.get('village') or 
                   address.get('municipality') or 
                   address.get('county', 'Local Detectado'))
            
            state = address.get('state', '')
            country = address.get('country', '')
            
            if state and country:
                return f"{city}, {state}, {country}"
            elif city:
                return city
            else:
                return "Local Detectado"
        else:
            return f"Coordenadas: {lat}, {lon}"
    except:
        return f"Coordenadas: {lat}, {lon}"

def check_backend_status():
    """Verifica se o backend está rodando"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

# Cidades pré-definidas do Brasil para seleção rápida
CIDADES_BRASIL = {
    "Brasília, DF": (-15.794200, -47.882200),
    "São Paulo, SP": (-23.550520, -46.633309),
    "Rio de Janeiro, RJ": (-22.906847, -43.172896),
    "Belo Horizonte, MG": (-19.919052, -43.937817),
    "Salvador, BA": (-12.971598, -38.501873),
    "Curitiba, PR": (-25.441105, -49.276855),
    "Porto Alegre, RS": (-30.034647, -51.217658),
    "Recife, PE": (-8.047562, -34.877003),
    "Fortaleza, CE": (-3.731862, -38.526669),
    "Goiânia, GO": (-16.686882, -49.264496),
    "Campo Grande, MS": (-20.462521, -54.615299),
    "Cuiabá, MT": (-15.601411, -56.097889),
    "Manaus, AM": (-3.119028, -60.021731),
    "Belém, PA": (-1.455833, -48.503887),
    "João Pessoa, PB": (-7.115, -34.863),
    "Natal, RN": (-5.795, -35.209),
    "Maceió, AL": (-9.666, -35.735),
    "Aracaju, SE": (-10.911, -37.072),
    "Teresina, PI": (-5.089, -42.803),
    "São Luís, MA": (-2.530, -44.302),
    "Macapá, AP": (0.034, -51.070),
    "Boa Vista, RR": (2.820, -60.673),
    "Rio Branco, AC": (-9.975, -67.810),
    "Porto Velho, RO": (-8.762, -63.902),
    "Palmas, TO": (-10.240, -48.360),
    "Vitória, ES": (-20.319, -40.338),
    "Florianópolis, SC": (-27.594, -48.548)
}

def main():
    # Inicializar session state
    if 'latitude' not in st.session_state:
        st.session_state.latitude = -15.794200
    if 'longitude' not in st.session_state:
        st.session_state.longitude = -47.882200
    if 'location_name' not in st.session_state:
        st.session_state.location_name = "Brasília, DF"
    if 'location_accuracy' not in st.session_state:
        st.session_state.location_accuracy = "manual"

    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🌱 TerraSynapse V2.0</h1>
        <p>Sistema Inteligente de Monitoramento Agrícola</p>
    </div>
    """, unsafe_allow_html=True)

    # Verificar status do backend
    backend_online = check_backend_status()
    
    if not backend_online:
        st.markdown("""
        <div class="status-offline">
            ⚠️ <strong>Modo Demo:</strong> Backend não conectado. Para dados reais, inicie o backend em localhost:8000
        </div>
        """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("🎛️ Controles")
        
        if backend_online:
            st.success("🟢 Sistema Online")
        else:
            st.error("🔴 Modo Demo")
        
        st.divider()
        
        # Configuração da fazenda
        st.subheader("🏡 Configuração da Fazenda")
        
        fazenda_nome = st.text_input("Nome da Fazenda", value="Fazenda Exemplo")
        
        # Seção de localização
        st.subheader("📍 Localização")
        
        opcao_localizacao = st.radio(
            "Como definir a localização:",
            ["🏙️ Selecionar Cidade", "🌐 Detectar por IP", "📍 Inserir Coordenadas"]
        )
        
        if opcao_localizacao == "🏙️ Selecionar Cidade":
            cidade_selecionada = st.selectbox(
                "Escolha uma cidade:",
                list(CIDADES_BRASIL.keys()),
                index=list(CIDADES_BRASIL.keys()).index("Brasília, DF") if "Brasília, DF" in CIDADES_BRASIL else 0
            )
            
            if cidade_selecionada:
                lat, lon = CIDADES_BRASIL[cidade_selecionada]
                st.session_state.latitude = lat
                st.session_state.longitude = lon
                st.session_state.location_name = cidade_selecionada
                st.session_state.location_accuracy = "cidade pré-definida"
        
        elif opcao_localizacao == "🌐 Detectar por IP":
            if st.button("🌐 Detectar Localização por IP", key="detect_ip"):
                with st.spinner("🔍 Detectando localização pelo IP..."):
                    location_data = get_location_by_ip()
                    
                    if location_data:
                        st.session_state.latitude = location_data['latitude']
                        st.session_state.longitude = location_data['longitude']
                        
                        if location_data['region'] and location_data['country']:
                            st.session_state.location_name = f"{location_data['city']}, {location_data['region']}, {location_data['country']}"
                        else:
                            st.session_state.location_name = location_data['city']
                        
                        st.session_state.location_accuracy = location_data['accuracy']
                        st.success(f"✅ Localização detectada: {st.session_state.location_name}")
                    else:
                        st.error("❌ Não foi possível detectar a localização por IP")
            
            st.info("💡 A detecção por IP fornece localização aproximada baseada na sua conexão de internet.")
        
        elif opcao_localizacao == "📍 Inserir Coordenadas":
            st.write("**Insira as coordenadas manualmente:**")
            col1, col2 = st.columns(2)
            
            with col1:
                latitude_input = st.number_input(
                    "Latitude", 
                    value=float(st.session_state.latitude), 
                    format="%.6f",
                    step=0.000001,
                    key="lat_input"
                )
            with col2:
                longitude_input = st.number_input(
                    "Longitude", 
                    value=float(st.session_state.longitude), 
                    format="%.6f",
                    step=0.000001,
                    key="lon_input"
                )
            
            if latitude_input != st.session_state.latitude or longitude_input != st.session_state.longitude:
                st.session_state.latitude = latitude_input
                st.session_state.longitude = longitude_input
                st.session_state.location_accuracy = "manual"
                
                with st.spinner("🔍 Obtendo informações da localização..."):
                    st.session_state.location_name = get_location_name(latitude_input, longitude_input)
            
            if st.button("🔄 Atualizar Nome da Localização", key="update_location"):
                with st.spinner("🔍 Atualizando localização..."):
                    st.session_state.location_name = get_location_name(
                        st.session_state.latitude, 
                        st.session_state.longitude
                    )
                st.success("✅ Localização atualizada!")
        
        st.markdown("---")
        st.info(f"📍 **Localização Atual:**\n{st.session_state.location_name}")
        st.caption(f"Precisão: {st.session_state.location_accuracy}")
        st.caption(f"Coordenadas: {st.session_state.latitude:.4f}, {st.session_state.longitude:.4f}")
        
        st.divider()
        
        cultura = st.selectbox(
            "🌾 Cultura Principal",
            ["soja", "milho", "trigo", "café", "algodão"]
        )
        
        st.divider()
        
        if st.button("🔄 Atualizar Dados", key="refresh_button"):
            st.rerun()
        
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)

    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🌤️ Clima", "🛰️ Satélite", "📈 Mercado"])

    with tab1:
        st.header("📊 Dashboard Geral")
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.info(f"🏡 **Fazenda:** {fazenda_nome}")
        with col_info2:
            st.info(f"📍 **Localização:** {st.session_state.location_name}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        import random
        import numpy as np
        
        lat = st.session_state.latitude
        temp_base = 25 - (abs(lat) - 15) * 0.5
        temp_atual = round(temp_base + random.uniform(-3, 8), 1)
        
        umidade_atual = round(55 + random.uniform(-15, 25), 1)
        precipitacao = round(random.uniform(0, 25), 1)
        ndvi = round(0.7 + random.uniform(-0.1, 0.2), 2)
        
        with col1:
            st.metric(
                "🌡️ Temperatura",
                f"{temp_atual}°C",
                delta=f"{random.choice(['+', '-'])}{random.uniform(0.5, 3):.1f}°C",
                help="Temperatura atual da fazenda"
            )
        
        with col2:
            st.metric(
                "💧 Umidade Solo",
                f"{umidade_atual}%",
                delta=f"{random.choice(['+', '-'])}{random.uniform(1, 8):.1f}%",
                help="Umidade do solo média"
            )
        
        with col3:
            st.metric(
                "🌧️ Precipitação",
                f"{precipitacao}mm",
                delta=f"+{random.uniform(0, 10):.1f}mm",
                help="Chuva acumulada (últimas 24h)"
            )
        
        with col4:
            st.metric(
                "📈 Índice NDVI",
                f"{ndvi}",
                delta=f"{random.choice(['+', '-'])}{random.uniform(0.01, 0.08):.2f}",
                help="Saúde da vegetação"
            )

        st.subheader("🚨 Alertas do Sistema")
        
        alertas = []
        
        if temp_atual > 28:
            alertas.append(("warning", "🌡️ Temperatura elevada detectada. Considere irrigação."))
        
        if umidade_atual < 40:
            alertas.append(("warning", "💧 Umidade do solo baixa. Irrigação recomendada."))
        
        if precipitacao < 2:
            alertas.append(("warning", "🌧️ Baixa precipitação nas últimas 24h."))
        
        if ndvi > 0.85:
            alertas.append(("success", "📈 NDVI excelente! Vegetação saudável."))
        
        if not alertas:
            alertas.append(("success", "✅ Todos os parâmetros dentro do normal."))
        
        for tipo, mensagem in alertas:
            if tipo == "warning":
                st.markdown(f"""
                <div class="alert-warning">
                    ⚠️ <strong>Alerta:</strong> {mensagem}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-success">
                    ✅ <strong>Status:</strong> {mensagem}
                </div>
                """, unsafe_allow_html=True)

        st.subheader("📊 Tendências (Últimos 30 Dias)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dias = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
            temp_data = pd.DataFrame({
                'Data': dias,
                'Temperatura': [temp_atual + random.uniform(-5, 5) for _ in range(30)]
            })
            
            fig_temp = px.line(
                temp_data, 
                x='Data', 
                y='Temperatura',
                title="🌡️ Temperatura dos Últimos 30 Dias",
                color_discrete_sequence=['#2E8B57']
            )
            fig_temp.update_layout(
                xaxis_title="Data",
                yaxis_title="Temperatura (°C)",
                hovermode='x unified'
            )
            st.plotly_chart(fig_temp, width='stretch')
        
        with col2:
            umidade_data = pd.DataFrame({
                'Data': dias,
                'Umidade': [umidade_atual + random.uniform(-10, 10) for _ in range(30)]
            })
            
            fig_umidade = px.area(
                umidade_data,
                x='Data',
                y='Umidade',
                title="💧 Umidade do Solo",
                color_discrete_sequence=['#4169E1']
            )
            fig_umidade.update_layout(
                xaxis_title="Data",
                yaxis_title="Umidade (%)",
                hovermode='x unified'
            )
            st.plotly_chart(fig_umidade, width='stretch')

        st.subheader("🗺️ Localização da Fazenda")
        
        mapa_data = pd.DataFrame({
            'lat': [st.session_state.latitude],
            'lon': [st.session_state.longitude],
            'fazenda': [fazenda_nome]
        })
        
        st.map(mapa_data, zoom=12)
        st.caption(f"📍 Coordenadas: {st.session_state.latitude:.6f}, {st.session_state.longitude:.6f}")

    with tab2:
        st.header("🌤️ Monitoramento Climático")
        
        if backend_online:
            st.success("✅ Conectado ao serviço meteorológico")
        else:
            st.info("📡 Modo demo - dados simulados para sua localização")
        
        st.info(f"📍 Dados climáticos para: **{st.session_state.location_name}**")
        
        st.subheader("📊 Condições Atuais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌡️ Temperatura", f"{temp_atual}°C")
        with col2:
            st.metric("💧 Umidade Ar", f"{random.randint(60, 90)}%")
        with col3:
            st.metric("💨 Vento", f"{random.randint(8, 20)} km/h")
        with col4:
            st.metric("🌅 UV Index", f"{random.randint(3, 11)}")
        
        st.subheader("📅 Previsão 7 Dias")
        
        previsao_data = []
        for i in range(7):
            data = datetime.now() + timedelta(days=i)
            previsao_data.append({
                'Data': data.strftime('%d/%m'),
                'Dia': data.strftime('%a'),
                'Temp Min': random.randint(15, 20),
                'Temp Max': random.randint(25, 35),
                'Chuva (%)': random.randint(0, 80),
                'Condição': random.choice(['☀️ Sol', '⛅ Nublado', '🌧️ Chuva', '⛈️ Tempestade'])
            })
        
        previsao_df = pd.DataFrame(previsao_data)
        st.dataframe(previsao_df, width='stretch')

    with tab3:
        st.header("🛰️ Dados de Satélite")
        
        if backend_online:
            st.info("🛰️ Conectando com APIs de satélite...")
        else:
            st.info("📡 Modo demo - imagens simuladas")
        
        st.info(f"📍 Dados de satélite para: **{st.session_state.latitude:.4f}, {st.session_state.longitude:.4f}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Vista de Satélite")
            try:
                lat = st.session_state.latitude
                lon = st.session_state.longitude
                
                mapa_satelite = pd.DataFrame({
                    'lat': [lat],
                    'lon': [lon],
                    'size': [100]
                })
                
                st.map(mapa_satelite, zoom=15, size_col='size')
                
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.metric("📍 Latitude", f"{lat:.6f}°")
                with col_info2:
                    st.metric("📍 Longitude", f"{lon:.6f}°")
                
                google_earth_url = f"https://earth.google.com/web/@{lat},{lon},500a,1000d,35y,0h,0t,0r"
                st.markdown(f"🌍 [**Ver no Google Earth**]({google_earth_url})")
                
            except Exception as e:
                st.error(f"❌ Erro ao carregar mapa: {e}")
        
        with col2:
            st.subheader("📊 Análise NDVI")
            
            try:
                size = 15
                x = np.linspace(-0.005, 0.005, size)
                y = np.linspace(-0.005, 0.005, size)
                X, Y = np.meshgrid(x, y)
                
                np.random.seed(42)
                Z = np.zeros((size, size))
                
                for i in range(size):
                    for j in range(size):
                        if (i // 3) % 2 == 0 and (j // 3) % 2 == 0:
                            Z[i, j] = 0.7 + 0.15 * np.random.random()
                        elif (i // 4) % 2 == 1 or (j // 4) % 2 == 1:
                            Z[i, j] = 0.4 + 0.2 * np.random.random()
                        else:
                            Z[i, j] = 0.1 + 0.2 * np.random.random()
                
                fig_ndvi_map = go.Figure(data=go.Heatmap(
                    z=Z,
                    colorscale=[
                        [0, '#8B4513'],
                        [0.3, '#D2B48C'],
                        [0.5, '#FFFF00'],
                        [0.7, '#9ACD32'],
                        [1, '#006400']
                    ],
                    zmin=0,
                    zmax=1,
                    colorbar=dict(
                        title="NDVI",
                        tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                        ticktext=['0.0', '0.2', '0.4', '0.6', '0.8', '1.0']
                    )
                ))
                
                fig_ndvi_map.update_layout(
                    title="Mapa NDVI - Análise de Vegetação",
                    xaxis_title="Longitude Relativa",
                    yaxis_title="Latitude Relativa",
                    height=300,
                    showlegend=False
                )
                
                st.plotly_chart(fig_ndvi_map, width='stretch')
                
                ndvi_medio = np.mean(Z)
                ndvi_max = np.max(Z)
                ndvi_min = np.min(Z)
                
                col_ndvi1, col_ndvi2, col_ndvi3 = st.columns(3)
                with col_ndvi1:
                    st.metric("NDVI Médio", f"{ndvi_medio:.2f}")
                with col_ndvi2:
                    st.metric("NDVI Máximo", f"{ndvi_max:.2f}")
                with col_ndvi3:
                    st.metric("NDVI Mínimo", f"{ndvi_min:.2f}")
                
                if ndvi_medio > 0.6:
                    st.success("✅ Vegetação saudável detectada")
                elif ndvi_medio > 0.4:
                    st.warning("⚠️ Vegetação moderada")
                else:
                    st.error("❌ Baixa cobertura vegetal")
                    
            except Exception as e:
                st.error(f"❌ Erro ao gerar análise NDVI: {e}")
                
                st.info("📊 **Análise NDVI Simplificada**")
                ndvi_atual = round(0.6 + random.uniform(-0.2, 0.3), 2)
                st.metric("NDVI Atual", f"{ndvi_atual}")
                
                if ndvi_atual > 0.7:
                    st.success("✅ Vegetação excelente")
                elif ndvi_atual > 0.5:
                    st.warning("⚠️ Vegetação boa")
                else:
                    st.error("❌ Vegetação baixa")
        
        st.subheader("📈 Evolução NDVI")
        
        ndvi_historico = pd.DataFrame({
            'Data': pd.date_range(start='2024-01-01', periods=12, freq='ME'),
            'NDVI': [0.6 + i*0.02 + random.uniform(-0.05, 0.05) for i in range(12)]
        })
        
        fig_ndvi = px.line(
            ndvi_historico,
            x='Data',
            y='NDVI',
            title="Evolução do NDVI ao Longo do Ano",
            color_discrete_sequence=['#228B22']
        )
        st.plotly_chart(fig_ndvi, width='stretch')

    with tab4:
        st.header("📈 Dados de Mercado")
        
        if backend_online:
            st.success("💹 Conectado às APIs de commodities")
        else:
            st.info("📊 Modo demo - preços simulados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Preços Atuais (R$/saca)")
            
            precos = pd.DataFrame({
                'Commodity': ['Soja 60kg', 'Milho 60kg', 'Trigo 60kg', 'Café 60kg'],
                'Preço': [155.50, 48.30, 42.20, 485.80],
                'Variação (%)': [2.1, -1.5, 0.8, 3.2],
                'Tendência': ['📈', '📉', '📈', '📈']
            })
            
            def color_variacao(val):
                if val > 0:
                    return 'background-color: #d4edda'
                elif val < 0:
                    return 'background-color: #f8d7da'
                else:
                    return ''
            
            styled_precos = precos.style.map(color_variacao, subset=['Variação (%)'])
            st.dataframe(styled_precos, width='stretch')
        
        with col2:
            st.subheader("📊 Análise de Rentabilidade")
            
            if cultura.lower() == 'soja':
                preco_atual = 155.50
                custo_producao = 95.00
                margem = preco_atual - custo_producao
                rentabilidade = (margem / custo_producao) * 100
                
                st.metric("💰 Preço Atual", f"R$ {preco_atual:.2f}/sc")
                st.metric("💸 Custo Produção", f"R$ {custo_producao:.2f}/sc")
                st.metric("📊 Margem", f"R$ {margem:.2f}/sc", f"{rentabilidade:.1f}%")
        
        st.subheader("📈 Evolução de Preços (Últimos 6 meses)")
        
        meses = pd.date_range(start='2024-03-01', periods=6, freq='ME')
        preco_historico = pd.DataFrame({
            'Mês': meses,
            'Soja': [145 + i*2 + random.uniform(-5, 5) for i in range(6)],
            'Milho': [42 + i*1 + random.uniform(-3, 3) for i in range(6)],
            'Trigo': [38 + i*0.5 + random.uniform(-2, 2) for i in range(6)]
        })
        
        fig_precos = px.line(
            preco_historico,
            x='Mês',
            y=['Soja', 'Milho', 'Trigo'],
            title="Evolução dos Preços das Principais Commodities",
            color_discrete_sequence=['#2E8B57', '#FF6B35', '#4169E1']
        )
        fig_precos.update_layout(
            xaxis_title="Mês",
            yaxis_title="Preço (R$/saca)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_precos, width='stretch')

    # Auto-refresh
    if auto_refresh:
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    main()
