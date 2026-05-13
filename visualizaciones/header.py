import streamlit as st

def render_header():
    urlLogo = "https://github.com/derekaraujo17/ProyectoASMAA/blob/desarrollo/frontend/assets/spibblePy.png?raw=true"
    st.markdown(f"""
    <div class="custom-header">
        <img src="{urlLogo}" class="logo" alt="logo Spibblepy">
        <span class="title">SpibblePy</span>
    </div>
    """, unsafe_allow_html=True)