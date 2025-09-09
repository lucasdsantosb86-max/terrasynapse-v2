import streamlit as st, pandas as pd, plotly.express as px
st.set_page_config(page_title="Clima", page_icon="⛅")
st.title("⛅ Monitoramento Climático")

weekly = pd.DataFrame([
    {"day":"Seg","temp":22,"humidity":65,"et0":3.8},
    {"day":"Ter","temp":25,"humidity":58,"et0":4.2},
    {"day":"Qua","temp":24,"humidity":62,"et0":4.0},
    {"day":"Qui","temp":26,"humidity":55,"et0":4.5},
    {"day":"Sex","temp":24,"humidity":68,"et0":4.2},
    {"day":"Sáb","temp":23,"humidity":72,"et0":3.9},
    {"day":"Dom","temp":25,"humidity":60,"et0":4.3},
])
fig = px.area(weekly, x="day", y=["temp","et0"], markers=True)
st.plotly_chart(fig, use_container_width=True)
