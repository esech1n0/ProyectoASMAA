import streamlit as st
import time
import random
from visualizaciones.header import render_header
from visualizaciones.helpers import leer_externos, obtener_imagen_base64


@st.cache_data(show_spinner=False)
def ejecutar_motor_json(archivos):
    from logica.motorjson import procesarDatosJson
    return procesarDatosJson(archivos)


@st.cache_data(show_spinner=False)
def ejecutar_motor_oauth(token):
    from logica.motoroauth import ticket
    return ticket(token)


def mostrar_pantalla_carga():
    if "analisis_listo" not in st.session_state:
        st.session_state["analisis_listo"] = False

    if "animacion_elegida" not in st.session_state:
        st.session_state["animacion_elegida"] = random.randint(1, 7)

    if "ui_renderizada" not in st.session_state:
        st.session_state["ui_renderizada"] = False

    numero = st.session_state["animacion_elegida"]

    try:
        cssGlobal = leer_externos("frontend/estilosGlobales.css")
        st.markdown(f"<style>{cssGlobal}</style>", unsafe_allow_html=True)
    except:
        pass

    if not st.session_state["analisis_listo"]:

        contenedorAnimacion = st.empty()

        rutasGifs = {
            1: "frontend/animacionCarga/links/pibble_edn.gif",
            2: "frontend/animacionCarga/links/starkirk.gif",
            3: "frontend/animacionCarga/links/tuff.gif",
            4: "frontend/animacionCarga/links/pibble_edn.gif",
            5: "frontend/animacionCarga/links/starkirk.gif",
            6: "frontend/animacionCarga/links/pibble_edn.gif",
            7: "frontend/animacionCarga/links/tuff.gif"
        }

        rutaGifElegida = rutasGifs.get(numero, rutasGifs[1])

        try:
            codigoCss = leer_externos("frontend/animacionCarga/carga.css")
            htmlCrudo = leer_externos("frontend/animacionCarga/carga.html")

            gif_base64 = obtener_imagen_base64(rutaGifElegida)

            htmlListo = htmlCrudo.replace("{{GIF_BASE64}}", gif_base64)

            paqueteCompleto = f"<style>{codigoCss}</style>{htmlListo}"

            contenedorAnimacion.markdown(paqueteCompleto, unsafe_allow_html=True)

            time.sleep(0.2)

        except:
            st.warning("Esperando archivos frontend")
            
        if not st.session_state["ui_renderizada"]:
            st.session_state["ui_renderizada"] = True
            st.rerun()

        with st.spinner():

            if st.session_state["motor"] == "motorjson":
                try:
                    inicio = time.time()

                    resultados = ejecutar_motor_json(st.session_state["jsonValidos"])
                    st.session_state["resultados"] = resultados

                    if time.time() - inicio < 10:
                        time.sleep(10 - (time.time() - inicio))

                    st.session_state["analisis_listo"] = True
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {e}")

            elif st.session_state["motor"] == "motoroauth":
                try:
                    inicio = time.time()

                    token = st.session_state.get("tokenSpotify")
                    resultados = ejecutar_motor_oauth(token)
                    st.session_state["resultados_oauth"] = resultados

                    if time.time() - inicio < 10:
                        time.sleep(10 - (time.time() - inicio))

                    st.session_state["analisis_listo"] = True
                    st.rerun()

                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        render_header()
        try:
            codigoCss = leer_externos("frontend/animacionCarga/carga.css")
            st.markdown(f"<style>{codigoCss}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            pass
        
        st.success("¡Pibble terminó de cocinar!")
        
        chef_b64 = obtener_imagen_base64("frontend/assets/pibble_chef.png")
        plato_b64 = obtener_imagen_base64("frontend/assets/plato.png")
        
        html_final = f"""
        <div class="contenedor-chef">
            <div class="escena">
                <img src="{chef_b64}" class="chef-img">
                <img src="{plato_b64}" class="plato-img">
            </div>
        </div>
        """
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown(html_final, unsafe_allow_html=True)
            
            col_b1, col_b2, col_b3 = st.columns([1, 1.5, 1])
            
            with col_b2:
                if st.button("SERVIR RESULTADOS", use_container_width=True):
                    if st.session_state["motor"] == "motorjson":
                        st.session_state["pantalla_actual"] = "dashboardjson"
                    elif st.session_state["motor"] == "motoroauth":
                        st.session_state["pantalla_actual"] = "dashboardoauth"
                    
                    st.session_state["analisis_listo"] = False
                    del st.session_state["animacion_elegida"]
                    del st.session_state["ui_renderizada"]
                    st.rerun()