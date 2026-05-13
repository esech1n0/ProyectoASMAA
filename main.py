from dotenv import load_dotenv
import streamlit as st

load_dotenv()
st.set_page_config(page_title="Spibblepy",layout="wide")
from visualizaciones import home, seleccion, dashboardjson, dashboardoauth, pantallaCarga

# inicialización de la memoria (st.session_state)
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if "pantalla_actual" not in st.session_state:
    st.session_state["pantalla_actual"] = "home"

if st.session_state["pantalla_actual"] == "home":
    home.mostrar_pantalla_pibble()

elif st.session_state["pantalla_actual"] == "seleccion":
    seleccion.mostrar_pantalla_botones()

elif st.session_state["pantalla_actual"] == "pantallaCarga":
    pantallaCarga.mostrar_pantalla_carga()

elif st.session_state["pantalla_actual"] == "dashboardjson":
    dashboardjson.mostrar_dashboardjson()
elif st.session_state["pantalla_actual"] == "dashboardoauth":
    dashboardoauth.mostrar_dashboardoauth()