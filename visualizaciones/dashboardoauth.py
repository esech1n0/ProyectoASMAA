import streamlit as st
from datetime import datetime
from visualizaciones.header import render_header
from visualizaciones.helpers import leer_externos
from visualizaciones.helpers import obtener_imagen_base64

def mostrar_dashboardoauth():
    render_header()
    datosTicket = st.session_state.get("resultados_oauth")

    if not datosTicket:
        st.error("No hay datos de spotify. Volviendo a la pantalla anterior...")
        st.session_state["pantalla_actual"] = "seleccion"
        st.rerun()
    try:
        cssGlobal = leer_externos("frontend/estilosGlobales.css")
        moldeHtml = leer_externos("frontend/animacionOauth/ticket.html")
        codigoCss = leer_externos("frontend/animacionOauth/ticket.css")
        st.markdown(f"<style>{cssGlobal}</style>", unsafe_allow_html=True)
        st.markdown(f"<style>{codigoCss}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Esperando archivos frontend")
        return
    htmlListaCanciones = ""
    for index, cancion in enumerate(datosTicket["canciones"]):
        renglon=f"""
        <div class="ticket-fila">
        <span class="ticket-num">{(index+1):02d}</span>
        <div class="ticket-info">
        <span class="ticket-cancion">{cancion["nombre"]}</span>
        <span class="ticket-artista">{cancion["artista"]}</span>
        </div>
        <span class="ticket-duracion">{cancion["duracion"]}</span>
        </div>
        """
        htmlListaCanciones += renglon
    fechaHoy = datetime.now().strftime("%d/%m/%Y %H:%M")
    nombre = datosTicket["nombre"]

    htmlFinal = moldeHtml.replace("{{FECHA_HOY}}",fechaHoy)
    htmlFinal = htmlFinal.replace("{{NOMBRE}}", nombre)
    htmlFinal = htmlFinal.replace("{{CANTIDAD_ITEMS}}", str(len(datosTicket["canciones"])))
    htmlFinal = htmlFinal.replace("{{LISTA_CANCIONES}}", htmlListaCanciones)
    htmlFinal = htmlFinal.replace('\n', '')
    
    pibbleCashier = obtener_imagen_base64("frontend/assets/pibble_cashier.png")
    st.markdown(f"""
    <div class="contenedor-ticket">
        <img src="{pibbleCashier}" class="pibble-cashier">
        {htmlFinal}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='border-color':rgba(255,255,255,0.1); margin:40px 0;'>", unsafe_allow_html=True)
    
    if st.button("Volver a elegir análisis",use_container_width=True):
        st.session_state["pantalla_actual"] = "seleccion"
        del st.session_state["resultados_oauth"]
        st.rerun()