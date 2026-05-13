import streamlit as st
import base64
import os

@st.cache_data(show_spinner=False)
def leer_externos(archivo):
    with open (archivo, "r", encoding="utf-8") as f:
        contenido = f.read()
    return contenido

@st.cache_data(show_spinner=False)
def obtener_imagen_base64(rutaImagen):
    _, extension = os.path.splitext(rutaImagen)
    tipo_mime = "gif" if extension.lower() == ".gif" else "png"
    try:
        with open(rutaImagen, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded_string}"
    except FileNotFoundError:
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="