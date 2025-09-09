import streamlit as st, pandas as pd
st.set_page_config(page_title="Mercado", page_icon="💹")
st.title("💹 Inteligência de Mercado")

df = pd.DataFrame([
    {"Produto":"Soja","Preço (R$/sc)":165.50,"Variação (%)":2.3},
    {"Produto":"Milho","Preço (R$/sc)":75.80,"Variação (%)":-1.2},
    {"Produto":"Café","Preço (R$/sc)":1089.30,"Variação (%)":4.1},
])
st.dataframe(df, use_container_width=True)
