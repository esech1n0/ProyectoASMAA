import streamlit as st
from visualizaciones.header import render_header
import os
import re 
import unicodedata
import base64
import random
from logica.motorjson import diccionarioVibras
from datetime import datetime, timedelta

def limpiar_nombre_pibble(nombrePibble):
    nombreLimpio = ''.join((c for c in unicodedata.normalize('NFD', nombrePibble) if unicodedata.category(c) != 'Mn'))
    nombreLimpio = re.sub(r'[^a-z0-9]', '_', nombreLimpio.lower())
    nombreLimpio = re.sub(r'_+', '_', nombreLimpio).strip('_')
    return nombreLimpio

def obtener_pibble_base64(nombreArtista, generoArtista):
    nombreArtista = limpiar_nombre_pibble(nombreArtista) 
    generoArtista = limpiar_nombre_pibble(generoArtista)
    
    rutaIdeal = f"frontend/assets/{nombreArtista}.png"
    rutaGenero = f"frontend/assets/{generoArtista}.png"
    rutaGenerico = f"frontend/assets/pibble_generico.png"

    rutaFinal = rutaIdeal if os.path.exists(rutaIdeal) else rutaGenero if os.path.exists(rutaGenero) else rutaGenerico 
    try:
        with open(rutaFinal, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except FileNotFoundError:
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="


def mostrar_dashboardjson():
    render_header()
    rutaCssGlobal = "frontend/estilosGlobales.css"
    rutaCssDiapositivas = "frontend/animacionJson/diapositiva.css"
    
    try:
        with open(rutaCssGlobal, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True) 
    except FileNotFoundError:
        with open(rutaCssDiapositivas, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        pass  
    resultados = st.session_state.get("resultados",None)

    if resultados is None:
        st.session_state["pantalla_actual"] = "seleccion"
        st.rerun()
    elif resultados:
        st.session_state["pantalla_actual"] = "dashboardjson"
        cancionesTop1, artistasTop1, resumenFeeling, dfTiempoMensual, top5Canciones, top5Artistas, dfArtistasSemanal, dfCancionesSemanal, tiempoSemanal = resultados

    meses=dfTiempoMensual["añoMesReproduccion"].unique().tolist()

    if not st.session_state.get("pantallaMes"):
        rutaHtmlDashboardjson = "frontend/animacionJson/dashboardjson.html"
        rutaCssDashboardjson = "frontend/animacionJson/dashboardjson.css"
        try:
            with open(rutaHtmlDashboardjson, "r", encoding="utf-8") as f:
                codigoHtml = f.read()
            with open(rutaCssDashboardjson, "r", encoding="utf-8") as f:
                codigoCss = f.read()
            st.markdown(f"<style>{codigoCss}</style>",unsafe_allow_html=True)
        except:
            st.warning(f"Esperando el archivo frontend")
        if st.button("Volver a la selección"):
            st.session_state["pantalla_actual"] = "seleccion"
            if "resultados" in st.session_state:
                del st.session_state["resultados"]
            if "jsonValidos" in st.session_state:
                del st.session_state["jsonValidos"]
            if "motor" in st.session_state:
                del st.session_state["motor"]
            st.rerun()
        cols = st.columns(3) 

        for index, mes in enumerate(meses):
            cancionesMes = cancionesTop1[cancionesTop1["añoMesReproduccion"]==mes]
            artistasMes = artistasTop1[artistasTop1["añoMesReproduccion"]==mes]
            feelingMes = resumenFeeling[resumenFeeling["añoMesReproduccion"]==mes]
            tiempoMes = dfTiempoMensual[dfTiempoMensual["añoMesReproduccion"]==mes]
            urlCancion = cancionesMes["urlPortada"].iloc[0] if not cancionesMes.empty else "sin_imagen_cancion.png"
            urlArtista = artistasMes["urlFoto"].iloc[0] if not artistasMes.empty else "sin_imagen_artista.png"
            emojiVibra = feelingMes["emoji"].iloc[0] if not feelingMes.empty else "🎶"
            porcentaje = tiempoMes["porcentajeReloj"].iloc[0] if not tiempoMes.empty else 0
            minutos = tiempoMes["minutosReproducidos"].iloc[0] if not tiempoMes.empty else 0
            porcentaje = int(porcentaje*100)
            nombreArtista = artistasMes["artistName"].iloc[0] if not artistasMes.empty else "Desconocido"
            generoArtista = artistasMes["vibraArtista"].iloc[0] if not artistasMes.empty else "Desconocido"
            imagenPibbleBase64 = obtener_pibble_base64(nombreArtista,generoArtista)
            tarjetaActual = codigoHtml

            tarjetaActual = tarjetaActual.replace("{{MES_ACTUAL}}",mes)
            tarjetaActual = tarjetaActual.replace("{{URL_CANCION}}",urlCancion)
            tarjetaActual = tarjetaActual.replace("{{URL_ARTISTA}}",urlArtista)
            tarjetaActual = tarjetaActual.replace("{{EMOJI_VIBRA}}",emojiVibra)
            tarjetaActual = tarjetaActual.replace("{{PORCENTAJE}}", str(porcentaje))
            tarjetaActual = tarjetaActual.replace("{{MINUTOS_TOTALES}}",str(minutos))
            tarjetaActual = tarjetaActual.replace("{{IMAGEN_PIBBLE}}",imagenPibbleBase64)  

            colActual = cols[index%3]
            with colActual:
                st.markdown(tarjetaActual, unsafe_allow_html=True)
                if st.button(f"Ver resumen de   {mes}", key=f"btn_{mes}", use_container_width=True):
                    st.session_state["pantallaMes"] = mes
                    st.rerun()
    else:
        mes = st.session_state["pantallaMes"]
        paso = st.session_state.setdefault("paso_historia",1)
        rutaCssDiapositivas = "frontend/animacionJson/diapositiva.css"
        try:
            with open(rutaCssDiapositivas, "r", encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            pass
        if paso == 1:
            rutaHtmlDiapositiva1="frontend/animacionJson/slideCancion.html"
            with open(rutaHtmlDiapositiva1, "r", encoding="utf-8") as f:
                moldeSlide = f.read()
            cancionesMes = cancionesTop1[cancionesTop1["añoMesReproduccion"]==mes]
            urlCancion1 = cancionesMes["urlPortada"].iloc[0] if not cancionesMes.empty else "sin_imagen_cancion.png"
            nombreCancion1 = cancionesMes["trackName"].iloc[0] if not cancionesMes.empty else "Desconocido"
            nombreArtista1 = cancionesMes["artistName"].iloc[0] if not cancionesMes.empty else "Desconocido"
            escuchas = cancionesMes["cantidadEscuchas"].iloc[0] if not cancionesMes.empty else 0
            slideActual = moldeSlide.replace("{{URL_CANCION}}", urlCancion1)
            slideActual = slideActual.replace("{{NOMBRE_CANCION}}",nombreCancion1)
            slideActual = slideActual.replace("{{NOMBRE_ARTISTA}}",nombreArtista1)
            slideActual = slideActual.replace("{{CANTIDAD_ESCUCHAS}}",str(escuchas))
            st.markdown(slideActual, unsafe_allow_html=True)
            if st.button("Siguiente paso: Tu artista top"):
                st.session_state["paso_historia"] = 2
                st.rerun()
        elif paso == 2:
            rutaHtmlDiapositiva2 = "frontend/animacionJson/slideArtista.html"
            with open(rutaHtmlDiapositiva2, "r", encoding="utf-8") as f:
                moldeSlide = f.read()
            artistasMes = artistasTop1[artistasTop1["añoMesReproduccion"]==mes]
            nombreArtista = artistasMes["artistName"].iloc[0] if not artistasMes.empty else "Desconocido"
            urlArtista = artistasMes["urlFoto"].iloc[0] if not artistasMes.empty else "sin_imagen_artista.png"
            generoArtista = artistasMes["vibraArtista"].iloc[0] if not artistasMes.empty else "🎶"
            imagenPibble = obtener_pibble_base64(nombreArtista, generoArtista)
            minutosArtista = artistasMes["minutosReproducidos"].iloc[0] if not artistasMes.empty else 0
            slideActual = moldeSlide.replace("{{IMAGEN_PIBBLE}}", imagenPibble)
            slideActual = slideActual.replace("{{URL_ARTISTA}}",urlArtista)
            slideActual = slideActual.replace("{{NOMBRE_ARTISTA}}", nombreArtista)
            slideActual = slideActual.replace("{{MINUTOS_TOTALES}}", str(minutosArtista))
            st.markdown(slideActual, unsafe_allow_html=True)
            if st.button("Siguiente paso: Tu vibra mensual"):
                st.session_state["paso_historia"] = 3
                st.rerun()
        elif paso == 3:
            rutaHtmlDiapositiva3 = "frontend/animacionJson/slideFeeling.html"
            with open(rutaHtmlDiapositiva3, "r", encoding="utf-8") as f:
                moldeSlide = f.read()
            feelingMes = resumenFeeling[resumenFeeling["añoMesReproduccion"]==mes]
            vibra = feelingMes["vibraDominante"].iloc[0] if not feelingMes.empty else "Desconocido"
            emoji = feelingMes["emoji"].iloc[0] if not feelingMes.empty else "🎶"
            slideActual = moldeSlide.replace("{{EMOJI_VIBRA}}", emoji)
            slideActual = slideActual.replace("{{NOMBRE_VIBRA}}", vibra)
            st.markdown(slideActual, unsafe_allow_html=True)
            if st.button("Siguiente paso: Tu tiempo total de escucha"):
                st.session_state["paso_historia"]=4
                st.rerun()
        elif paso == 4:
            rutaHtmlDiapositiva4 = "frontend/animacionJson/slideTiempo.html"
            with open(rutaHtmlDiapositiva4, "r", encoding="utf-8") as f:
                moldeSlide = f.read()
            tiempoMes = dfTiempoMensual[dfTiempoMensual["añoMesReproduccion"]==mes]
            minutosTotales = tiempoMes["minutosReproducidos"].iloc[0] if not tiempoMes.empty else 0
            diasTotales = round(minutosTotales/1440,1)
            slideActual = moldeSlide.replace("{{MINUTOS_TOTALES}}",str(minutosTotales))
            slideActual = slideActual.replace("{{DIAS_TOTALES}}",str(diasTotales))
            st.markdown(slideActual, unsafe_allow_html=True)
            if st.button("Resumen completo"):
                st.session_state["paso_historia"] = 5
                st.rerun()
        elif paso == 5:
            rutaHtmlDiapositiva5 = "frontend/animacionJson/slideCompleto.html"
            with open(rutaHtmlDiapositiva5, "r",encoding="utf-8") as f:
                moldeSlide = f.read()
            cancionesDelMes = top5Canciones[top5Canciones["añoMesReproduccion"]==mes]
            htmlListaCanciones = ""
            for index, fila in cancionesDelMes.iterrows():
                urlCancion = fila["urlPortada"]
                nombreCancion = fila["trackName"]
                nombreArtista = fila["artistName"]
                elementoLi = f'<li class="elemento-lista"><img class="slide-completo-lista" src="{urlCancion}"><p class="nombre-cancion">{nombreCancion} de {nombreArtista}</p></li>'
                htmlListaCanciones += elementoLi
            artistasDelMes = top5Artistas[top5Artistas["añoMesReproduccion"]==mes]
            htmlListaArtistas = ""
            for index, fila in artistasDelMes.iterrows():
                urlArtista = fila["urlFoto"]
                nombreArtista = fila["artistName"]
                minutos = fila["minutosReproducidos"]
                elementoLi = f'<li class="elemento-lista"><img class="slide-completo-lista" src="{urlArtista}"><p class="nombre-artista">{nombreArtista} con un total de <span class="minutos-artista">{minutos}</span> minutos</p></li>'
                htmlListaArtistas += elementoLi
            feelingMes = resumenFeeling[resumenFeeling["añoMesReproduccion"]==mes]
            vibra = feelingMes["vibraDominante"].iloc[0] if not feelingMes.empty else "Desconocido"
            emoji = feelingMes["emoji"].iloc[0] if not feelingMes.empty else "🎶"
            frasesCreativas = {
                # --- CULTURA HIP-HOP Y CALLE ---
                "🎤 Rap & Hip-Hop": ["Barras, beats y flow sin parar.","Escupiendo rimas todo el mes.","El bombo y la caja marcan el ritmo de tus días.","Leyendas del micrófono en repetición constante."],
                "🔥 Trap & Drill": ["Rompiendo el bajo en cada bocina.", "Modo calle activado este mes.","Mucho fronteo, hi-hats rápidos y actitud.","El sub-bajo retumba, la energía no baja."],
                # --- URBANO Y REGIONAL LATINO ---
                "🥵 Urbano Latino": ["Perreo intenso hasta abajo y sin miedo.","El dembow domina tus playlists.","Flow latino que pone a vibrar la calle.","Cero estrés, mucho reggaetón y buenas vibras."],
                "🌮 Regional & Corridos": ["Pura guitarra sierreña y trompetas al cien.","Corridos que cuentan historias de principio a fin.","Con el sombrero puesto y la música a todo volumen.","Sentimiento ranchero que llega directo al pecho."],
                "🌴 Tropical & Fiestero": ["Azúcar, sabor y ritmo que obliga a bailar.","Cumbia, salsa y bachata para mover los pies.","Tu mes fue una fiesta caribeña constante.","Clave, güiro y mucho movimiento en la pista."], 
                # --- POP Y TENDENCIAS ---
                "🪩 Pop Mainstream": ["Tus gustos están en el top de las listas.", "Pura energía pop para alegrar el día.","Estribillos pegadizos que cantaste a todo pulmón.","Los hits mundiales son la banda sonora de tu vida."],
                "🌸 K-Pop & Asiático": ["Coreografías perfectas y melodías adictivas.","Todo un idol: tu mes estuvo lleno de brillo asiático.","Vocales increíbles y conceptos visuales en tu cabeza.","Fandom activado, apoyando a tus grupos favoritos."],
                # --- NOSTALGIA Y ROMANCE ---
                "🍷 Romántico & Cortavenas": ["Un mes para cantarle al desamor (o al amor).", "Preparando los pañuelos y las baladas.","Letras profundas que pegan justo en el sentimiento.","Dedicando canciones y suspirando con cada acorde."],
                "📻 Nostalgia Retro": ["Un viaje en el tiempo a las mejores décadas doradas.","Los clásicos nunca mueren, y tu historial lo demuestra.","Hombreras, bolas de disco y sintetizadores vintage.","Como escuchar la radio en los viejos y buenos tiempos."],
                # --- ENERGÍA Y CLUB ---
                "⚡ Electrónica & Club": ["El drop perfecto te acompañó en cada momento.","BPMs altos para mantener la energía a tope.","Sintetizadores y luces de neón en tu mente.","Tu habitación se convirtió en el escenario principal."], 
                # --- GUITARRAS Y BATERÍAS ---
                "🎸 Rock Clásico & Hard": ["Solos de guitarra legendarios y mucha distorsión.","El espíritu del rock and roll sigue más vivo que nunca.","Baterías pesadas y actitud rebelde en tus oídos.","Levanta los cuernos, este mes fue puro poder eléctrico."],
                "🖤 Metal & Oscuridad": ["Doble bombo, riffs pesados y mucha agresividad.","Oscuridad y volumen al máximo sin pedir permiso.","Rompiendo cuellos con los breakdowns más brutales.","Intensidad pura que hace temblar las paredes."],
                "🌿 Indie & Alternativo": ["Fuera del mainstream, directo al alma.", "Guitarras suaves y mucha onda.","Descubriendo joyas ocultas y sonidos diferentes.","Melancolía bonita y letras que te hacen pensar."],
                "🏕️ Country & Folk": ["Guitarras acústicas e historias junto a la fogata.","Raíces profundas y voces honestas cantando verdades.","Un respiro tranquilo con sabor a madera y naturaleza.","Melodías de carretera para viajes largos y atardeceres."],
                # --- CHILL, SOUL Y RELAJACIÓN ---
                "🎷 Soul & R&B": ["Voces sedosas y bajos que te hacen mover la cabeza.","Mucho groove, sentimiento puro y ritmos elegantes.","Vibras aterciopeladas para relajar cuerpo y mente.","El lado más sensual y emotivo de la música."],
                "☁️ Chill & Lo-Fi": ["Beats relajados para estudiar, trabajar o solo existir.","Una taza de café, lluvia en la ventana y cero estrés.","Frecuencias bajas que calman la ansiedad del día a día.","El soundtrack perfecto para dejar la mente en blanco."],
                "☕ Jazz & Blues": ["Improvisación, saxofones y acordes complejos.","La tristeza del blues transformada en arte puro.","Sofisticación musical en tiempos asincopados.","Elegancia clásica que nunca pasa de moda."],
                # --- CONCENTRACIÓN Y ESTUDIO ---
                "🎻 Clásica & Instrumental": ["Sinfonías magistrales y concentración absoluta.","Bandas sonoras épicas que elevan cualquier momento.","El poder de la música sin necesidad de una sola palabra.","Pianos, violines y arreglos que acarician el espíritu."],
                # --- EL CASO NEUTRAL (EMPATE TOTAL) ---
                "🔀 Variado": ["Un poquito de todo: no te casas con un solo género.","Tu historial es un caos hermoso de diferentes mundos.","Pasas del reggaetón al rock sin escalas y sin culpa.","¿Por qué elegir uno cuando puedes escucharlos todos?"]
            }
            listaFrases = frasesCreativas.get(vibra, ["Tus gustos musicales son únicos."])
            fraseElegida = random.choice(listaFrases)
            palabrasDeVibra = diccionarioVibras.get(vibra, ["Tu estilo único"])
            cantidadGeneros = min(3, len(palabrasDeVibra))
            generosElegidos = random.sample(palabrasDeVibra, cantidadGeneros)
            textoGenerosClave = ", ".join(generosElegidos).title()
            tiempoMes = dfTiempoMensual[dfTiempoMensual["añoMesReproduccion"]==mes]
            minutosTotales = tiempoMes["minutosReproducidos"].iloc[0] if not tiempoMes.empty else 0
            tipoDato = random.choice(["rango","equivalencia"])
            if tipoDato == "rango":
                tituloCurioso = "Tu rango de oyente 🏆"
                if minutosTotales < 2000:
                    textoCurioso = "Explorador sonoro: Escuchas música para acompañar tus momentos, pero sin obsesionarte."
                elif minutosTotales < 6000:
                    textoCurioso = "Amante de la música: Tus audífonos son una parte muy importante de tu rutina diaria."
                elif minutosTotales <12000:
                    textoCurioso = "Melómano empedernido: Hay música sonando en tu cabeza casi todo el día"
                else:
                    textoCurioso = "Vives en spotify 👽: Prácticamente respiras música. Tus estadísticas no son de este planeta"
            else:
                tituloCurioso = "¿A qué equivale tu tiempo de escucha?"
                opcionEquivalencia = random.choice(["shrek", "vuelos", "partidos","baños"])
                if opcionEquivalencia == "shrek":
                    veces = int(minutosTotales//90)
                    textoCurioso = f"En lugar de escuchar música, podrías haber visto la primera película de Shrek {veces} veces este mes"
                elif opcionEquivalencia == "vuelos":
                    veces = int(minutosTotales//660)
                    textoCurioso = f"Ese tiempo en música equivale a subirte a un avión y volar a Europa unas {veces} seguidas"
                elif opcionEquivalencia == "partidos":
                    veces = int(minutosTotales//90)
                    textoCurioso = f"Tu tiempo de escucha es exactamente lo que durarían {veces} partidos de fútbol consecutivos"
                else:
                    textoCurioso = f"Ese tiempo es menor al de esperar por un baño limpio en CUCEI"

            slideActual = moldeSlide.replace("{{MES_ACTUAL}}", mes)
            slideActual = slideActual.replace("{{LISTA_CANCIONES}}", htmlListaCanciones)
            slideActual = slideActual.replace("{{LISTA_ARTISTAS}}", htmlListaArtistas)
            slideActual = slideActual.replace("{{EMOJI_VIBRA}}",emoji)
            slideActual = slideActual.replace("{{NOMBRE_VIBRA}}",vibra)
            slideActual = slideActual.replace("{{FRASE_ALEATORIA}}", fraseElegida)
            slideActual = slideActual.replace("{{GENEROS_CLAVE}}",textoGenerosClave)
            slideActual = slideActual.replace("{{MINUTOS_TOTALES}}",f"{minutosTotales:,}")
            slideActual = slideActual.replace("{{DATO_CURIOSO_TITULO}}", tituloCurioso)
            slideActual = slideActual.replace("{{DATO_CURIOSO_TEXTO}}",textoCurioso)

            slideActual = slideActual.replace('\n', '')
            st.markdown(slideActual, unsafe_allow_html=True)
            
            st.markdown("<h2 class='slide-completo-titulo' style='margint-top:60px;'>Tus semanas de este mes</h2>",unsafe_allow_html=True)
            artistasSemanaMes = dfArtistasSemanal[dfArtistasSemanal["añoMesReproduccion"]==mes]
            semanasDelMes = sorted(artistasSemanaMes["semanaReproduccion"].unique())
            columnasSemanas = st.columns(min(3, len(semanasDelMes)))
            for index, semana in enumerate(semanasDelMes):
                añoIso, numSemanaIso = semana.split('-')
                fechaInicioSemana = datetime.strptime(f"{añoIso}-W{numSemanaIso}-1","%G-W%V-%u")
                fechaFinSemana = fechaInicioSemana + timedelta(days=6)
                mesesEspañolAbrev = ["ene", "feb", "mar", "abr", "may", "jun","jul","ago","sep","oct","nov","dic"]
                strInicio = f"{fechaInicioSemana.day} {mesesEspañolAbrev[fechaInicioSemana.month-1]}"
                strFin = f"{fechaFinSemana.day} {mesesEspañolAbrev[fechaFinSemana.month-1]}"
                rangoFechas = f"{strInicio} al {strFin}"
                top3Semana = artistasSemanaMes[artistasSemanaMes["semanaReproduccion"]==semana]
                htmlFotos = ""
                for url in top3Semana["urlFoto"]:
                    htmlFotos += f'<img src="{url}" class="foto-semana">'
                tarjetaSemana = f"""
                <div class="contenedor-semana">
                <div class="semana-titulo">Semana {index+1}</div>
                <div class="semana-fechas">{rangoFechas}</div> <div class="fotos-top3-semana">
                {htmlFotos}
                </div>
                </div>"""
                colActual = columnasSemanas[index % 3]
                with colActual:
                    st.markdown(tarjetaSemana, unsafe_allow_html=True)
                    if st.button(f"Explorar semana", key=f"btn_sem_{semana}", use_container_width=True):
                        st.session_state["semana_elegida"] = semana
                        st.session_state["paso_historia"] = 6
                        st.rerun()
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 40px 0;'></hr>",unsafe_allow_html=True)
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin:40px 0;'>",unsafe_allow_html=True)
            if st.button("Volver al resumen de todos los meses",use_container_width=True):
              del st.session_state["pantallaMes"]
              del st.session_state["paso_historia"]
              st.rerun()  
        elif paso == 6:
            semana = st.session_state["semana_elegida"]
            rutaHtmlDiapositiva6 = "frontend/animacionJson/slideSemanal.html"
            with open(rutaHtmlDiapositiva6, "r", encoding="utf-8") as f:
                moldeSlide = f.read()
            artistasSemana = dfArtistasSemanal[dfArtistasSemanal["semanaReproduccion"]==semana]
            cancionesSemana = dfCancionesSemanal[dfCancionesSemanal["semanaReproduccion"]==semana]
            datosTiempo = tiempoSemanal[tiempoSemanal["semanaReproduccion"]==semana]
            añoIso, numSemanaIso = semana.split('-')
            fechaInicioSemana = datetime.strptime(f"{añoIso}-W{numSemanaIso}-1","%G-W%V-%u")
            fechaFinSemana = fechaInicioSemana + timedelta(days=6)
            mesesEspañolAbrev = ["ene", "feb", "mar", "abr", "may", "jun","jul","ago","sep","oct","nov","dic"]
            strInicio = f"{fechaInicioSemana.day} {mesesEspañolAbrev[fechaInicioSemana.month-1]}"
            strFin = f"{fechaFinSemana.day} {mesesEspañolAbrev[fechaFinSemana.month-1]}"
            rangoFechas = f"{strInicio} al {strFin}"            
            htmlListaArtistas = ""
            for index, fila in artistasSemana.head(3).iterrows():
                urlFoto = fila["urlFoto"]
                nombreArtista = fila["artistName"]
                minutos = fila["totalMinutosArt"]
                htmlListaArtistas += f'<li class="elemento-lista"><img class="slide-completo-lista" src="{urlFoto}"><p class="nombre-artista">{nombreArtista} <br><span class="minutos-artista">{minutos:,} min</span></p></li>'
                
            htmlListaCanciones = ""
            for index, fila in cancionesSemana.head(3).iterrows():
                urlPortada = fila["urlPortada"]
                nombreCancion = fila["trackName"]
                nombreArtista = fila["artistName"]
                htmlListaCanciones += f'<li class="elemento-lista"><img class="slide-completo-lista" src="{urlPortada}"><p class="nombre-cancion">{nombreCancion} <br><span style="font-size: 14px; opacity: 0.7;">de {nombreArtista}</span></p></li>'
                
            minutosTotales = datosTiempo["totalMinutosSem"].iloc[0] if not datosTiempo.empty else 0
            
            cancionesTotales = datosTiempo["cantidadEscuchasSem"].iloc[0] if not datosTiempo.empty else 0 

            slideActual = moldeSlide.replace("{{NUM_SEMANA}}", numSemanaIso)
            slideActual = slideActual.replace("{{RANGO_FECHAS}}", rangoFechas)
            slideActual = slideActual.replace("{{LISTA_ARTISTAS}}", htmlListaArtistas)
            slideActual = slideActual.replace("{{LISTA_CANCIONES}}", htmlListaCanciones)
            slideActual = slideActual.replace("{{MINUTOS_TOTALES}}", f"{int(minutosTotales):,}")
            slideActual = slideActual.replace("{{CANCIONES_TOTALES}}", f"{int(cancionesTotales):,}")
            
            slideActual = slideActual.replace('\n', '')
            st.markdown(slideActual, unsafe_allow_html=True)

            st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 40px 0;'>", unsafe_allow_html=True)
            if st.button("Volver al mes", use_container_width=True):
                st.session_state["paso_historia"] = 5  
                st.rerun()            

            if st.button("Volver al resumen de todos los meses", key="btn_volver_meses_paso6" ,use_container_width=True):
                del st.session_state["pantallaMes"]
                del st.session_state["paso_historia"]
                st.rerun()
                