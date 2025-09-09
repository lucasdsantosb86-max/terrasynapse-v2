import os
import streamlit as st
import requests

st.set_page_config(page_title='TerraSynapse', page_icon='🌱', layout='wide')
st.title('🌱 TerraSynapse — Streamlit OK')
st.success('Frontend básico rodando. Agora podemos integrar a API, gráficos e login.')

API_URL = os.getenv('TS_API_URL', 'https://terrasynapse-backend.onrender.com')  # ajuste se for outro
try:
    r = requests.get(f"{API_URL}/health", timeout=5)
    st.write('API status:', r.status_code, r.text[:200])
except Exception as e:
    st.info('Não consegui falar com a API ainda. Configure TS_API_URL no Render.')
