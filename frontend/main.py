from streamlit_geolocation import geolocation
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------------------------
# CONFIG DA PÁGINA
# -------------------------------------------------------------------
st.set_page_config(
    page_title="TerraSynapse - Plataforma Agrícola Enterprise",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------------
# CONFIG / SECRETS
# - BACKEND_URL: pega de secrets -> env -> default local
# - SITE (lat/lon): pega de secrets -> sessão -> IP geo -> fallback BR
# -------------------------------------------------------------------
def _get_secret(section: str, key: str, default: Optional[str] = None):
    try:
        return st.secrets.get(section, {}).get(key, default)
    except Exception:
        return default

BACKEND_URL = (
    _get_secret("api", "API_BASE_URL")
    or os.getenv("API_BASE_URL")
    or "http://localhost:8000"
)

DEFAULT_LAT = float(_get_secret("site", "lat", "-15.7942"))
DEFAULT_LON = float(_get_secret("site", "lon", "-47.8822"))
DEFAULT_TZ  = _get_secret("site", "timezone", "auto")
SITE_NAME   = _get_secret("site", "name", "Propriedade")

# -------------------------------------------------------------------
# HELPERS HTTP
# -------------------------------------------------------------------
def fazer_requisicao(
    endpoint: str,
    method: str = "GET",
    data: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None,
    timeout: int = 20,
) -> Optional[Dict[str, Any]]:
    """Cliente HTTP simples para o backend."""
    url = f"{BACKEND_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if method.upper() == "GET":
            resp = requests.get(url, headers=headers, timeout=timeout)
        elif method.upper() == "POST":
            resp = requests.post(url, json=data or {}, headers=headers, timeout=timeout)
        else:
            raise ValueError("Método HTTP não suportado")

        # Tenta devolver o JSON sempre que possível, com o status junto
        payload = {}
        try:
            payload = resp.json()
        except Exception:
            payload = {"detail": resp.text or "Sem corpo."}

        payload["_status_code"] = resp.status_code
        if resp.status_code >= 400:
            # Mostra erro amigável
            st.error(f"API {resp.status_code} em {endpoint}: {payload.get('detail')}")
        return payload

    except requests.exceptions.Timeout:
        st.warning("⏳ Tempo limite excedido (timeout). O serviço pode estar acordando.")
        return None
    except requests.exceptions.ConnectionError as e:
        st.error(f"🔌 Erro de conexão com a API: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Erro inesperado na requisição: {e}")
        return None

# -------------------------------------------------------------------
# GEOLOCALIZAÇÃO / LOCAL
# -------------------------------------------------------------------
def geolocalizacao_por_ip() -> Tuple[float, float, str, str]:
    """Tenta obter lat/lon/cidade/estado via IP. Fallback: Brasília."""
    try:
        r = requests.get("http://ip-api.com/json/", timeout=8)
        if r.status_code == 200:
            d = r.json()
            return float(d["lat"]), float(d["lon"]), d.get("city", ""), d.get("region", "")
    except Exception:
        pass
    return DEFAULT_LAT, DEFAULT_LON, "Brasília", "DF"

def obter_localizacao():
    """
    1) tenta obter a posição via navegador (precisa https e permissão do usuário)
    2) se o usuário negar ou falhar, usa valor salvo na sidebar (se houver)
    3) como último recurso, usa um fallback fixo
    """
    # 1) geolocalização do navegador
    loc = geolocation(key="geo_btn", refresh_button_text="Atualizar localização")
    if loc and loc.get("latitude") and loc.get("longitude"):
        return float(loc["latitude"]), float(loc["longitude"]), "Local atual", ""

    # 2) tentativa: se você tiver guardado algo no session_state
    if "user_lat" in st.session_state and "user_lon" in st.session_state:
        return float(st.session_state.user_lat), float(st.session_state.user_lon), "Coordenadas salvas", ""

    # 3) fallback (ex.: Brasília)
    return -15.7942, -47.8822, "Brasília", "DF"
    # 1) sessão
    if "lat" in st.session_state and "lon" in st.session_state:
        return (
            float(st.session_state.lat),
            float(st.session_state.lon),
            st.session_state.get("cidade", SITE_NAME) or SITE_NAME,
            st.session_state.get("estado", ""),
        )
    # 2) secrets
    if DEFAULT_LAT and DEFAULT_LON:
        return DEFAULT_LAT, DEFAULT_LON, SITE_NAME, ""
    # 3) IP
    return geolocalizacao_por_ip()

# -------------------------------------------------------------------
# ESTADO DE SESSÃO
# -------------------------------------------------------------------
for k, v in {
    "logged_in": False,
    "user_token": None,
    "user_data": None,
}.items():
    st.session_state.setdefault(k, v)

# -------------------------------------------------------------------
# HEADER
# -------------------------------------------------------------------
st.title("🌾 TerraSynapse V2.0")
st.subheader("Plataforma Enterprise de Monitoramento Agrícola")
st.caption(f"Backend: `{BACKEND_URL}`")
st.divider()

# -------------------------------------------------------------------
# SIDEBAR: LOGIN / CADASTRO / STATUS
# -------------------------------------------------------------------
with st.sidebar:
    st.header("🔐 Portal Executivo")

    if not st.session_state.logged_in:
        tab_login, tab_reg = st.tabs(["🔑 Login", "👤 Cadastro"])

        with tab_login:
            st.subheader("Acesso Executivo")
            email = st.text_input("📧 Email Corporativo", key="login_email")
            password = st.text_input("🔒 Senha", type="password", key="login_password")

            if st.button("🚀 Entrar", type="primary", use_container_width=True):
                if not email or not password:
                    st.warning("⚠️ Preencha email e senha.")
                else:
                    with st.spinner("🔄 Autenticando..."):
                        # tenta /login e /auth/login (depende da sua API)
                        result = (
                            fazer_requisicao("/login", "POST", {"email": email, "password": password})
                            or fazer_requisicao("/auth/login", "POST", {"email": email, "password": password})
                        )
                    if result and result.get("access_token"):
                        st.session_state.logged_in = True
                        st.session_state.user_token = result["access_token"]
                        st.session_state.user_data = result.get("user", {"nome": email})
                        st.success("✅ Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Credenciais inválidas ou API indisponível.")

        with tab_reg:
            st.subheader("Registro Enterprise")
            nome = st.text_input("👤 Nome Completo", key="reg_nome")
            email_reg = st.text_input("📧 Email", key="reg_email")
            password_reg = st.text_input("🔒 Senha", type="password", key="reg_password")
            perfil = st.selectbox(
                "🎯 Perfil Profissional",
                [
                    "Produtor Rural",
                    "Agrônomo",
                    "Técnico Agrícola",
                    "Consultor",
                    "Cooperativa",
                    "Gerente Agrícola",
                    "Outro",
                ],
            )
            empresa = st.text_input("🏢 Empresa", key="reg_empresa")
            cidade = st.text_input("🌍 Cidade", key="reg_cidade")
            estado = st.selectbox(
                "📍 Estado",
                [
                    "SP","MG","MT","GO","MS","PR","RS","SC","BA","TO","MA","PI","CE","RN","PB","PE",
                    "AL","SE","ES","RJ","AC","RO","AM","RR","PA","AP","DF",
                ],
            )

            if st.button("🎯 Criar Conta Enterprise", type="primary", use_container_width=True):
                if nome and email_reg and password_reg:
                    with st.spinner("🔄 Criando conta..."):
                        result = (
                            fazer_requisicao(
                                "/register",
                                "POST",
                                {
                                    "nome_completo": nome,
                                    "email": email_reg,
                                    "password": password_reg,
                                    "perfil_profissional": perfil,
                                    "empresa_propriedade": empresa,
                                    "cidade": cidade,
                                    "estado": estado,
                                },
                            )
                            or fazer_requisicao(
                                "/auth/register",
                                "POST",
                                {
                                    "nome_completo": nome,
                                    "email": email_reg,
                                    "password": password_reg,
                                    "perfil_profissional": perfil,
                                    "empresa_propriedade": empresa,
                                    "cidade": cidade,
                                    "estado": estado,
                                },
                            )
                        )
                    if result and result.get("access_token"):
                        st.session_state.logged_in = True
                        st.session_state.user_token = result["access_token"]
                        st.session_state.user_data = result.get("user", {"nome": nome})
                        st.success("✅ Conta criada com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro no cadastro.")
                else:
                    st.warning("⚠️ Preencha os campos obrigatórios.")

    else:
        st.success(f"👋 Bem-vindo, {st.session_state.user_data.get('nome', 'Usuário')}!")
        st.info("🟢 Sistema Online")

        # Expander para configurar localização manual
        with st.expander("📍 Configurar Localização"):
            lat_default, lon_default, _, _ = obter_localizacao()
            st.session_state.lat = st.number_input("Latitude", value=float(lat_default), format="%.6f")
            st.session_state.lon = st.number_input("Longitude", value=float(lon_default), format="%.6f")
            if st.button("Salvar local", use_container_width=True):
                st.success("Localização atualizada.")
                st.rerun()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_token = None
            st.session_state.user_data = None
            st.rerun()

# -------------------------------------------------------------------
# CONTEÚDO
# -------------------------------------------------------------------
if st.session_state.logged_in:
    lat, lon, cidade, estado = obter_localizacao()
    st.info(f"📍 Localização: {cidade or SITE_NAME} • {lat:.4f}, {lon:.4f}")

    colA, colB = st.columns([1, 1])
    with colA:
        if st.button("🔄 Atualizar Dados", type="primary"):
            st.rerun()
    with colB:
        auto_refresh = st.checkbox("⚡ Auto-refresh (30s)")
    if auto_refresh:
        # Evita travar a UI se a API estiver lenta; usa um "sleep" curto
        time.sleep(30)
        st.rerun()

    st.divider()

    # DASHBOARD
    with st.spinner("🔄 Carregando inteligência agrícola..."):
        dashboard_data = fazer_requisicao(
            f"/dashboard/{lat}/{lon}",
            token=st.session_state.user_token,
        )

    if dashboard_data and dashboard_data.get("status") == "success":
        data = dashboard_data["data"]

        # ----- MÉTRICAS -----
        st.header("📊 Dashboard Executivo - Tempo Real")
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            temp = data.get("clima", {}).get("temperatura", "-")
            umi  = data.get("clima", {}).get("umidade", "-")
            st.metric("🌡️ Temperatura", f"{temp}°C", delta=f"Umidade: {umi}%")

        with c2:
            et0 = float(data.get("clima", {}).get("et0", 0) or 0)
            st.metric("💧 ET0", f"{et0:.2f} mm/dia", delta=("Crítico" if et0 > 6 else "Normal"))

        with c3:
            ndvi = float(data.get("vegetacao", {}).get("ndvi", 0) or 0)
            status_veg = data.get("vegetacao", {}).get("status_vegetacao", "")
            st.metric("🌱 NDVI", f"{ndvi:.3f}", delta=status_veg)

        with c4:
            receita = float(data.get("rentabilidade", {}).get("receita_por_hectare", 0) or 0)
            prod = data.get("rentabilidade", {}).get("produtividade_estimada", "-")
            st.metric("💰 Receita/ha", f"R$ {receita:,.0f}", delta=f"{prod} sc/ha")

        st.divider()

        # ----- ALERTAS -----
        st.header("⚠️ Centro de Alertas Inteligentes")
        alertas = data.get("alertas", []) or []
        if alertas:
            for a in alertas:
                msg = a.get("mensagem", "Alerta")
                pr  = (a.get("prioridade") or "").lower()
                if pr == "alta":
                    st.error(f"🚨 {msg}")
                elif pr == "media":
                    st.warning(f"⚠️ {msg}")
                else:
                    st.info(f"ℹ️ {msg}")
        else:
            st.success("✅ SISTEMA OPERACIONAL: Nenhum alerta crítico detectado.")

        st.divider()

        # ----- GRÁFICOS -----
        st.header("📈 Análise Técnica Avançada")
        g1, g2 = st.columns(2)

        with g1:
            st.subheader("🌡️ Evapotranspiração (ET0)")
            fig_gauge = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=float(et0),
                    title={"text": "ET0 (mm/dia)"},
                    delta={"reference": 5},
                    gauge={
                        "axis": {"range": [None, 10]},
                        "bar": {"color": "#2E7D32"},
                        "steps": [
                            {"range": [0, 3], "color": "lightgray"},
                            {"range": [3, 6], "color": "yellow"},
                            {"range": [6, 10], "color": "red"},
                        ],
                        "threshold": {
                            "line": {"color": "red", "width": 4},
                            "thickness": 0.75,
                            "value": 6,
                        },
                    },
                )
            )
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with g2:
            st.subheader("📈 Preços de Commodities")
            commodities = data.get("mercado", {}) or {}
            df_precos = pd.DataFrame(
                [
                    {"Commodity": "Soja", "Preço": commodities.get("soja", {}).get("preco", 0)},
                    {"Commodity": "Milho", "Preço": commodities.get("milho", {}).get("preco", 0)},
                    {"Commodity": "Café",  "Preço": commodities.get("cafe",  {}).get("preco", 0)},
                ]
            )
            fig_bar = px.bar(
                df_precos,
                x="Commodity",
                y="Preço",
                title="Preços Atuais (R$/saca)",
                color="Preço",
                color_continuous_scale="Greens",
            )
            fig_bar.update_layout(height=300)
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # ----- TABS DETALHES -----
        st.header("🔬 Análise Técnica Executiva")
        t1, t2, t3 = st.tabs(["🌡️ Climatologia", "🌱 Vegetação", "💰 Mercado"])

        with t1:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("📊 Condições Meteorológicas")
                clima = data.get("clima", {})
                st.write(f"**Temperatura:** {clima.get('temperatura', '-')}°C")
                st.write(f"**Umidade:** {clima.get('umidade', '-')}%")
                st.write(f"**Vento:** {clima.get('vento', '-')} km/h")
                st.write(f"**Pressão:** {clima.get('pressao', '-')} hPa")
                st.write(f"**Condição:** {clima.get('descricao', '-')}")

            with c2:
                st.subheader("💧 Gestão de Irrigação")
                et0_val = float(clima.get("et0", 0) or 0)
                recomend = clima.get("recomendacao_irrigacao", "—")
                st.write(f"**ET0:** {et0_val:.2f} mm/dia")
                st.write(f"**Recomendação:** {recomend}")
                if et0_val > 6:
                    st.error("🚨 ET0 elevada - Irrigação urgente recomendada")
                elif et0_val > 4:
                    st.warning("⚠️ ET0 moderada - Monitorar necessidade de irrigação")
                else:
                    st.success("✅ ET0 baixa - Irrigação não necessária")

        with t2:
            c1, c2 = st.columns(2)
            vegetacao = data.get("vegetacao", {})
            with c1:
                st.subheader("🛰️ Análise NDVI")
                st.write(f"**Valor:** {float(vegetacao.get('ndvi', 0) or 0):.3f}")
                st.write(f"**Status:** {vegetacao.get('status_vegetacao', '—')}")
                st.write(f"**Data:** {vegetacao.get('data_analise', '—')}")

            with c2:
                st.subheader("📋 Recomendações Técnicas")
                st.info(vegetacao.get("recomendacao", "—"))
                ndvi_val = float(vegetacao.get("ndvi", 0) or 0)
                if ndvi_val > 0.7:
                    st.success("🌟 Vegetação saudável e vigorosa")
                elif ndvi_val > 0.5:
                    st.info("📈 Vegetação em desenvolvimento normal")
                elif ndvi_val > 0.3:
                    st.warning("📉 Vegetação com estresse moderado")
                else:
                    st.error("🚨 Vegetação em estado crítico")

        with t3:
            st.subheader("📈 Análise de Mercado")
            for commodity, info in (data.get("mercado", {}) or {}).items():
                col1, col2, col3 = st.columns(3)
                preco = float(info.get("preco", 0) or 0)
                vari = float(info.get("variacao", 0) or 0)
                with col1:
                    st.metric(commodity.title(), f"R$ {preco:.2f}/saca")
                with col2:
                    st.metric("Variação", f"{vari:+.2f}%")
                with col3:
                    if commodity == "soja":
                        prod_est = float(data.get("rentabilidade", {}).get("produtividade_estimada", 0) or 0)
                        st.metric("Receita/ha", f"R$ {preco * prod_est:,.0f}")

        st.divider()

        # ----- CALCULADORA -----
        st.header("🧮 Calculadora Enterprise de Rentabilidade")
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            area_ha = st.number_input("🌾 Área (hectares)", min_value=1, value=10, step=1)
        with cc2:
            cultura_select = st.selectbox("🌱 Cultura Principal", ["Soja", "Milho", "Café"])
        with cc3:
            produtividade = st.number_input("📊 Produtividade (sacas/ha)", min_value=1, value=50, step=1)

        mercado = data.get("mercado", {})
        if cultura_select.lower() in mercado:
            preco_cultura = float(mercado[cultura_select.lower()].get("preco", 0) or 0)
            receita_total = area_ha * produtividade * preco_cultura
            custo_por_ha = 3000  # ajustar quando tiver custos reais
            custo_total = area_ha * custo_por_ha
            lucro_total = receita_total - custo_total
            margem = (lucro_total / receita_total) * 100 if receita_total > 0 else 0

            st.subheader(f"💰 Projeção Financeira - {cultura_select}")
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric("Receita Total", f"R$ {receita_total:,.0f}")
            with mc2:
                st.metric("Custo Estimado", f"R$ {custo_total:,.0f}")
            with mc3:
                st.metric("Lucro Projetado", f"R$ {lucro_total:,.0f}")

            st.caption(
                f"Área: {area_ha} ha | Produtividade: {produtividade} sc/ha | "
                f"Preço: R$ {preco_cultura:.2f}/saca | Margem: {margem:.1f}%"
            )

        st.divider()
        st.write(
            f"**TerraSynapse V2.0** — Última atualização: "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | 🟢 Sistema Online"
        )

    else:
        st.error("❌ Erro ao carregar dados do dashboard.")
        st.info("🔄 Verifique se o backend está online e o token válido.")
else:
    # LANDING SIMPLES (deslogado)
    st.header("🌾 TerraSynapse V2.0 Enterprise")
    st.subheader("Plataforma Líder em Inteligência Agrícola")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**🌡️ Monitoramento Climático** — ET0, recomendações de irrigação e métricas em tempo real.")
        st.write("**🛰️ Análise por Satélite** — NDVI e saúde da vegetação com alertas automáticos.")
    with col2:
        st.write("**💰 Inteligência de Mercado** — preços e tendências com projeções de rentabilidade.")
        st.write("**📊 Dashboard Executivo** — visão 360° da propriedade com relatórios.")
    st.info("🚀 Faça login na barra lateral para acessar os dados da sua propriedade.")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.metric("🌡️ Temperatura", "24.5°C", "Ideal para cultivo")
    with d2:
        st.metric("🌱 NDVI", "0.75", "Vegetação saudável")
    with d3:
        st.metric("💰 Soja", "R$ 165.50/sc", "+2.3%")

# -------------------------------------------------------------------
# DIAGNÓSTICO RÁPIDO
# -------------------------------------------------------------------
if st.sidebar.button("🔧 Diagnóstico do Sistema", use_container_width=True):
    with st.spinner("🔄 Verificando serviços..."):
        health = fazer_requisicao("/health")
        if health:
            st.sidebar.success("✅ APIs TerraSynapse Online")
            st.sidebar.json(health)
        else:
            st.sidebar.error("❌ Sistema Temporariamente Indisponível")
