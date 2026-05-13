import streamlit as st
import os
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
import base64
from visualizaciones.helpers import leer_externos, obtener_imagen_base64


spotifyOauth=SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="user-top-read user-read-recently-played",
    cache_handler=MemoryCacheHandler()
)

def mostrar_pantalla_pibble():
    rutaCssGlobal = "frontend/estilosGlobales.css"
    try: 
        cssGlobal = leer_externos(rutaCssGlobal)
        st.markdown(f"<style>{cssGlobal}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    
    st.markdown("""
                <h1 style="
                margin-top: -80px;
                text-align: center;
                font-size: clamp(2.0rem, 6vw, 3.0rem);
                font-family: 'Press Start 2P', cursive;
                color: #ffffff;
                text-shadow: 0 0 10px #8a2be2, 0 0 20px #a855f7;
                margin-bottom: 20px;
                animation: bounce 3s infinite;
                ">SpibblePy</h1>""", unsafe_allow_html=True)
    if "code" in st.query_params:
        #guardamos el código que spotify regresa en la url  lo guardamos en la variable codigoAutorizacion, un "ticket" que nos dará acceso a los datos
        codigoAutorizacion = st.query_params["code"] #query:params es un diccionario de streamlit que lee la url de la barra superior del navegador
        
        #intercambiamos el código temporal que nos regresa Spotify con Spotipy y nos devuelva la información del token real
        infoToken = spotifyOauth.get_access_token(codigoAutorizacion)

        #guardamos este token en la memoria de la aplicación para poder usarla en siguientes pantallas
        st.session_state["tokenSpotify"] = infoToken["access_token"]

        #limpiamos la url para que el próximo usuario pueda autenticarse sin problema
        st.query_params.clear()
        st.session_state["autenticado"] = True
        st.session_state["pantalla_actual"] = "seleccion"
        st.rerun()
    #la primera vez que entra un usuario
    urlAutorizacion = spotifyOauth.get_authorize_url()
    
    rutaHtml = "frontend/homeJuegoPibble/pibble.html"
    rutaCss = "frontend/homeJuegoPibble/pibble.css"
    rutaJs = "frontend/homeJuegoPibble/pibble.js"
    try:
        codigoHtml = leer_externos(rutaHtml)
        codigoCss = leer_externos(rutaCss)
        codigoJs = leer_externos(rutaJs)
        pibbleSuciob64 = obtener_imagen_base64("frontend/assets/pibble_sucio.png")
        pibbleLimpiob64 = obtener_imagen_base64("frontend/assets/pibble_limpio.png")
        estropajob64 = obtener_imagen_base64("frontend/assets/estropajo.png")
        htmlFinal = codigoHtml.replace("urlspotiaqui", urlAutorizacion)
        htmlFinal = htmlFinal.replace("{{PIBBLE_SUCIO}}", pibbleSuciob64)
        htmlFinal = htmlFinal.replace("{{PIBBLE_LIMPIO}}",pibbleLimpiob64)
        codigoCss = codigoCss.replace("{{ESTROPAJO}}", estropajob64)

        paqueteCompleto = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="color-scheme" content="dark light">
            <style>
                html, body {{
                    background-color:transparent !important;
                    background:transparent !important;
                    color-scheme:dark;
                    margin:0;
                    padding:0;
                    touch-action: none;
                }}
            </style>
            <style>{cssGlobal}</style>
            <style>{codigoCss}</style>
        </head>
        <body>
            {htmlFinal}
            <script>{codigoJs}</script>
        </body>
        </html>
        """
        htmlb64 = base64.b64encode(paqueteCompleto.encode('utf-8')).decode('utf-8')
        iframeCode = f'''<iframe
        src="data:text/html;base64,{htmlb64}"
        width="100%"
        style="height: 800px; min-height: 700px; border:none; background:transparent; overflow:hidden;"
        scrolling="no"
        sandbox="allow-scripts allow-same-origin allow-top-navigation"
        ></iframe>'''
        st.markdown(iframeCode, unsafe_allow_html=True)    
    except:
        st.warning(f"Esperando el archivo frontend")