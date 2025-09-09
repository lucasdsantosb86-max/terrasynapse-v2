import streamlit as st
from services.market import get_commodities

st.set_page_config(page_title="Mercado", page_icon="📈", layout="wide")
st.title("📈 Preços de Commodities (ao vivo)")

df = get_commodities()
for _, row in df.iterrows():
    col1, col2, col3 = st.columns([3,2,2])
    col1.markdown(f"**{row['name']}**  \n_ticker:_ `{row['ticker']}`")
    col2.metric("Preço", f"{row['price']:.2f}")
    chg = row['change_pct']
    col3.metric("Variação", f"{chg:+.2f}%")
    st.divider()
