import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pylast
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

#credenciales de spotify
clientId = os.getenv("SPOTIFY_CLIENT_ID")
clientSecret = os.getenv("SPOTIFY_CLIENT_SECRET")
credenciales = SpotifyClientCredentials(client_id=clientId,client_secret=clientSecret)
sp = spotipy.Spotify(auth_manager=credenciales)

#credenciales de last.fm
apiKey = os.getenv("LASTFM_API_KEY")
apiSecret = os.getenv("LASTFM_API_SECRET")
network = pylast.LastFMNetwork(api_key=apiKey, api_secret=apiSecret)

#base de datos con caché de las búsquedas realizadas
DATABASE_URL = os.getenv("DATABASE_URL")

def obtener_conexion():
    return psycopg2.connect(DATABASE_URL)

def inicializardb():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    #tabla para las imágenes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS imagenes_cache (
                   id_busqueda TEXT PRIMARY KEY,
                   url_imagen TEXT,
                   fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    #tabla para los géneros
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS generos_cache(
                   nombre_artista TEXT PRIMARY KEY,
                   texto_generos TEXT,
                   fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')    
    conexion.commit()
    cursor.close()
    conexion.close()

diccionarioVibras = {
    # --- CULTURA HIP-HOP Y CALLE ---
    "🎤 Rap & Hip-Hop": ["rap", "hip-hop", "hip hop", "boom bap", "underground hip-hop", "conscious hip hop", "east coast", "west coast"],
    "🔥 Trap & Drill": ["trap", "drill", "emo rap", "cloud rap", "southern hip hop", "atlanta", "trap argentino", "trap latino"],
    # --- URBANO Y REGIONAL LATINO ---
    "🥵 Urbano Latino": ["reggaeton", "dembow", "latin trap", "urbano latino", "perreo", "pop urbano"],
    "🌮 Regional & Corridos": ["corridos tumbados", "corridos", "nortenas", "regional mexicano", "banda", "mariachi", "ranchera", "mexico"],
    "🌴 Tropical & Fiestero": ["salsa", "cumbia", "bachata", "merengue", "tropical", "cumbia sonidera"],
    
    # --- POP Y TENDENCIAS ---
    "🪩 Pop Mainstream": ["pop", "dance pop", "electropop", "top 40", "teen pop", "commercial", "pop latino", "latin pop"],
    "🌸 K-Pop & Asiático": ["k-pop", "j-pop", "korean", "japanese", "anime", "idol"],
    
    # --- NOSTALGIA Y ROMANCE ---
    "🍷 Romántico & Cortavenas": ["bolero", "baladas", "romantico", "amor", "jose jose", "spanish", "cancion de autor", "cantautor"],
    "📻 Nostalgia Retro": ["70s", "80s", "90s", "00s", "disco", "oldies", "retro", "classic"],
    
    # --- ENERGÍA Y CLUB ---
    "⚡ Electrónica & Club": ["electronic", "house", "techno", "edm", "dance", "trance", "dubstep", "drum and bass", "electro"],
    
    # --- GUITARRAS Y BATERÍAS ---
    "🎸 Rock Clásico & Hard": ["rock", "classic rock", "hard rock", "blues rock", "arena rock", "rock en espanol", "rock nacional", "latin rock"],   
    "🖤 Metal & Oscuridad": ["metal", "heavy metal", "death metal", "black metal", "nu metal", "metalcore", "thrash metal"],
    "🌿 Indie & Alternativo": ["indie", "indie rock", "indie pop", "alternative", "alternative rock", "shoegaze", "post-punk", "new wave", "latin alternative", "indie latino", "indie argentino", "indie mexicano"],
    "🏕️ Country & Folk": ["country", "folk", "americana", "bluegrass", "singer-songwriter", "acoustic"],
    
    # --- CHILL, SOUL Y RELAJACIÓN ---
    "🎷 Soul & R&B": ["rnb", "r&b", "soul", "funk", "neo soul", "motown", "rhythm and blues"],
    "☁️ Chill & Lo-Fi": ["lo-fi", "chill", "chillout", "ambient", "downtempo", "relax", "bedroom pop"],
    "☕ Jazz & Blues": ["jazz", "blues", "smooth jazz", "bossa nova", "vocal jazz", "swing"],
    
    # --- CONCENTRACIÓN Y ESTUDIO ---
    "🎻 Clásica & Instrumental": ["classical", "instrumental", "soundtrack", "piano", "orchestral", "composer", "easy listening", "soft rock"]
}
def calcularVibra(listaTextosGeneros):
    puntuacion = {vibra: 0 for vibra in diccionarioVibras.keys()}
    for texto in listaTextosGeneros:
        if texto not in ["sin clasificar","no encontrado"]:
            etiquetasIndividuales = [tag.strip() for tag in texto.split(",")]
            #se reparten los puntos
            for tag in etiquetasIndividuales:
                for vibra, palabrasClave in diccionarioVibras.items():
                    if tag in palabrasClave:
                        puntuacion[vibra]+=1
                        #break #si ya encontró la categoría, pasa a la siguiente etiqueta
    #vibra ganadora
    vibraGanadora = max(puntuacion, key=puntuacion.get)
    #vibra neutral
    if puntuacion[vibraGanadora] == 0:
        return "🔀 Variado"
    
    return vibraGanadora

def obtenerImagenes(artist,track=None,cursor=None,memoria_imagenes=None):
    if cursor is None or memoria_imagenes is None:
        raise ValueError("Se necesita un cursor activo y la memoria de imágenes para consultar la base de datos")
    if track:
        id_busqueda = f"track:{artist}-{track}"
    else:
        id_busqueda = f"artist:{artist}"
    
    if id_busqueda in memoria_imagenes:
        return memoria_imagenes[id_busqueda]
    urlFinal = "sin imagen"

    try:
        if track:
            resultado = sp.search(q=f"artist:{artist} track:{track}",type="track",limit=1)
            urlFinal = resultado['tracks']['items'][0]['album']['images'][0]['url']
        else:
            resultado = sp.search(q=f"artist:{artist}",type="artist",limit=1)
            urlFinal=resultado['artists']['items'][0]['images'][0]['url']
    except Exception as e:
            urlFinal = "sin imagen"
    cursor.execute('''
                   INSERT INTO imagenes_cache (id_busqueda, url_imagen, fecha_actualizacion)
                   VALUES (%s, %s, NOW())
                   ON CONFLICT (id_busqueda)
                   DO UPDATE SET url_imagen = EXCLUDED.url_imagen, fecha_actualizacion = NOW()'''
                   ,(id_busqueda, urlFinal))
    memoria_imagenes[id_busqueda] = urlFinal
    return urlFinal

#obtener los géneros
def obtenerGeneros(artist,cursor=None, memoria_generos=None):
    if cursor is None or memoria_generos is None:
        raise ValueError("Se necesita un cursor activo y un memoria_generos")
    if artist in memoria_generos:
        return memoria_generos[artist]

    texto_generos = "sin clasificar"
    try:
        artist_lastfm = network.get_artist(artist)
        top_tags = artist_lastfm.get_top_tags(limit=5)
        listaGeneros = [tag.item.get_name().lower() for tag in top_tags]
        texto_generos = ", ".join(listaGeneros) if listaGeneros else "sin clasificar"
    except Exception as e:
        texto_generos = "no encontrado"
    
    cursor.execute('''
                   INSERT INTO generos_cache (nombre_artista, texto_generos, fecha_actualizacion)
                   VALUES (%s, %s, NOW())
                   ON CONFLICT (nombre_artista)
                   DO UPDATE SET texto_generos = EXCLUDED.texto_generos, fecha_actualizacion = NOW()
                   ''', (artist, texto_generos))
    memoria_generos[artist] = texto_generos    
    return texto_generos

#MÓDULO 1: "Historial completo". Utiliza datos json 

def procesarDatosJson(archivosSubidos):
    inicializardb()
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT id_busqueda, url_imagen FROM imagenes_cache WHERE fecha_actualizacion > NOW() - INTERVAL '30 days' ")
    memoria_imagenes = dict(cursor.fetchall())

    cursor.execute("SELECT nombre_artista, texto_generos FROM generos_cache WHERE fecha_actualizacion > NOW() - INTERVAL '30 days' ")
    memoria_generos = dict(cursor.fetchall())

    listadf = []
    mesesEspañol = {
        1:"Enero", 2:"Febrero", 3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
        7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"
    }
    for archivo in archivosSubidos:
        dfTemporal = pd.read_json(archivo)
        listadf.append(dfTemporal)
    dfSpotify = pd.concat(listadf, ignore_index=True)

    #limpieza de canciones que no sirven
    umbralMs = 30000 #umbral de tiempo mínimo de reproducción
    filasAntes = len(dfSpotify)
    dfLimpio = dfSpotify[dfSpotify["msPlayed"]>=umbralMs]
    filasDespues = len(dfLimpio)

    #se hace una copia del df para no modificar el original
    dfLimpio = dfLimpio.copy()
    #creación de columnas dentro de este df copia para obtener mes, día y hora de reproducción, usando la columna "endTime" como referencia
    dfLimpio["endTime"] = pd.to_datetime(dfLimpio["endTime"])
    mes = dfLimpio["endTime"].dt.month.map(mesesEspañol)
    año = dfLimpio["endTime"].dt.year.astype(str)
    dfLimpio["añoMesReproduccion"] = (mes + " " + año) 
    dfLimpio["semanaReproduccion"] = dfLimpio["endTime"].dt.strftime('%G-%V')
    dfLimpio["msPlayed"] = dfLimpio["msPlayed"]/60000
    dfLimpio = dfLimpio.rename(columns={"msPlayed":"minutosReproducidos"})
    dfLimpio["minutosReproducidos"]=dfLimpio["minutosReproducidos"].round(0).astype(int)
    dfLimpio["ordenTemporal"] = dfLimpio["endTime"].dt.strftime('%Y%m').astype(int)

    #TIEMPO DE ESCUCHA MENSUAL
    #agrupación por mes de reproducción y suma del tiempo de reproducción, obteniendo así el total de escucha por mes
    dfTiempoMensual = dfLimpio.groupby(["añoMesReproduccion","ordenTemporal"])["minutosReproducidos"].sum().reset_index() #esto regresa una serie donde el índice será el mes, y el valor es la suma de los ms
    dfTiempoMensual = dfTiempoMensual.sort_values(by="ordenTemporal",ascending=True)
    #promedio de tiempo por mes
    maximoMinutos = dfTiempoMensual["minutosReproducidos"].max()
    dfTiempoMensual["porcentajeReloj"] = dfTiempoMensual["minutosReproducidos"]/maximoMinutos
    
    #ARTISTAS MÁS ESCUCHADOS
    #agrupación por artistas más escuchados
    dfArtistasMensual = dfLimpio.groupby(["añoMesReproduccion","artistName","ordenTemporal"])["minutosReproducidos"].sum().reset_index()
    dfArtistasMensual =dfArtistasMensual.sort_values(by=["ordenTemporal","minutosReproducidos"],ascending=[True,False])
    top5Artistas =dfArtistasMensual.groupby("añoMesReproduccion").head().copy()
    
    top5Artistas["urlFoto"] = top5Artistas["artistName"].apply(lambda artist: obtenerImagenes(artist, track=None, cursor=cursor,memoria_imagenes=memoria_imagenes))

    #CANCIONES MÁS ESCUCHADAS
    dfCancionesMensual = dfLimpio.groupby(["añoMesReproduccion","trackName","artistName","ordenTemporal"]).agg(
        totalMinutos = ("minutosReproducidos","sum"),
        cantidadEscuchas = ("trackName","count")
    ).reset_index()
    dfCancionesMensual=dfCancionesMensual.sort_values(by=["ordenTemporal","totalMinutos"],ascending=[True,False])
    top5Canciones=dfCancionesMensual.groupby("añoMesReproduccion").head().copy()
    top5Canciones["urlPortada"] = top5Canciones.apply(lambda fila: obtenerImagenes(fila["artistName"],fila["trackName"],cursor=cursor,memoria_imagenes=memoria_imagenes),axis=1)
    
    #RESUMEN SEMANAL
    tiempoSemanal = dfLimpio.groupby(["añoMesReproduccion","semanaReproduccion","ordenTemporal"]).agg(
        totalMinutosSem = ("minutosReproducidos","sum"),
        cantidadEscuchasSem = ("trackName","count")
    ).reset_index()
    tiempoSemanal = tiempoSemanal.sort_values(by=["ordenTemporal","semanaReproduccion"],ascending=[True,True])
    
    dfCancionesSemanal = dfLimpio.groupby(["añoMesReproduccion","semanaReproduccion","trackName","artistName","ordenTemporal"]).agg(
        totalMinutos = ("minutosReproducidos","sum"),
        cantidadEscuchas = ("trackName","count")
    ).reset_index()
    dfCancionesSemanal = dfCancionesSemanal.sort_values(by=["ordenTemporal", "añoMesReproduccion","semanaReproduccion","totalMinutos"],ascending=[True,True,True,False])
    dfCancionesSemanal = dfCancionesSemanal.groupby(["añoMesReproduccion","semanaReproduccion"]).head(3).copy()
    
    dfArtistasSemanal = dfLimpio.groupby(["añoMesReproduccion","semanaReproduccion","artistName","ordenTemporal"]).agg(
        totalMinutosArt = ("minutosReproducidos","sum")
    ).reset_index()
    dfArtistasSemanal = dfArtistasSemanal.sort_values(by=["ordenTemporal", "añoMesReproduccion","semanaReproduccion","totalMinutosArt"],ascending=[True,True,True,False])
    dfArtistasSemanal = dfArtistasSemanal.groupby(["añoMesReproduccion","semanaReproduccion"]).head(3).copy()
    
    dfArtistasSemanal["urlFoto"] = dfArtistasSemanal["artistName"].apply(lambda artist: obtenerImagenes(artist, track=None, cursor=cursor, memoria_imagenes=memoria_imagenes))

    dfCancionesSemanal["urlPortada"] = dfCancionesSemanal.apply(lambda fila: obtenerImagenes(fila["artistName"],fila["trackName"],cursor=cursor,memoria_imagenes=memoria_imagenes),axis=1)

    #FEELING MENSUAL
    top20CancionesMensual = dfCancionesMensual.groupby(["añoMesReproduccion","ordenTemporal"]).head(20).copy()
    top20CancionesMensual["generos"] = top20CancionesMensual["artistName"].apply(lambda artist: obtenerGeneros(artist, cursor=cursor,memoria_generos = memoria_generos))

    feelingMensual = top20CancionesMensual.groupby(["añoMesReproduccion","ordenTemporal"])[["generos"]].agg(list).reset_index()

    feelingMensual["vibraDominante"] = feelingMensual["generos"].apply(calcularVibra)
    feelingMensual["emoji"] = feelingMensual["vibraDominante"].str[0]
    feelingMensual = feelingMensual.sort_values(by="ordenTemporal",ascending=True)
    resumenFeeling = feelingMensual[["añoMesReproduccion","ordenTemporal", "vibraDominante","emoji"]]

    #canciones top 1
    cancionesTop1 = top5Canciones.groupby("añoMesReproduccion").head(1).copy()
    cancionesTop1["urlPortada"] = cancionesTop1.apply(lambda fila: obtenerImagenes(fila["artistName"],fila["trackName"],cursor=cursor, memoria_imagenes=memoria_imagenes),axis=1)
    
    #artistas top 1
    artistasTop1 = top5Artistas.groupby("añoMesReproduccion").head(1).copy()
    artistasTop1["urlFoto"] = artistasTop1["artistName"].apply(lambda artist: obtenerImagenes(artist, track=None, cursor=cursor, memoria_imagenes=memoria_imagenes))
    artistasTop1["generosCrudos"] = artistasTop1["artistName"].apply(lambda artist: obtenerGeneros(artist, cursor=cursor,memoria_generos=memoria_generos))
    artistasTop1["vibraArtista"] = artistasTop1["generosCrudos"].apply(lambda generos: calcularVibra([generos]))

    cancionesTop1 = cancionesTop1.tail(12)
    artistasTop1 = artistasTop1.tail(12)
    resumenFeeling = resumenFeeling.tail(12)
    dfTiempoMensual = dfTiempoMensual.tail(12)

    mesesValidos = dfTiempoMensual["añoMesReproduccion"].tolist()
    top5Canciones = top5Canciones[top5Canciones["añoMesReproduccion"].isin(mesesValidos)]
    top5Artistas = top5Artistas[top5Artistas["añoMesReproduccion"].isin(mesesValidos)]
    dfArtistasSemanal = dfArtistasSemanal[dfArtistasSemanal["añoMesReproduccion"].isin(mesesValidos)]
    dfCancionesSemanal = dfCancionesSemanal[dfCancionesSemanal["añoMesReproduccion"].isin(mesesValidos)]
    tiempoSemanal = tiempoSemanal[tiempoSemanal["añoMesReproduccion"].isin(mesesValidos)]

    conexion.commit()
    cursor.close()
    conexion.close()
    
    return cancionesTop1, artistasTop1, resumenFeeling, dfTiempoMensual, top5Canciones, top5Artistas, dfArtistasSemanal, dfCancionesSemanal,tiempoSemanal

if __name__ == "__main__":
    import glob
    pd.set_option('display.max_columns',None)
    pd.set_option('display.max_colwidth', None)  
    pd.set_option('display.max_rows', None)    
    pd.set_option('display.width', 1000)
    rutaBase = os.getenv("RUTA_DATOS_SPOTIFY", "datosSpoti")    
    patronBusqueda = os.path.join(rutaBase, "*", "StreamingHistory_music_*.json")
    archivosPrueba = glob.glob(patronBusqueda) #cambiar la ruta por la ruta de sus archivos
    
    if not archivosPrueba:
        print("No se encontraron archivos JSON en la carpeta.")
    else:
        print(f"Procesando {len(archivosPrueba)} archivos... Esto puede tomar unos segundos debido a la API de Spotify.")
        
        cancionesTop1, artistasTop1, resumenFeeling, dfTiempoMensual, top5Canciones, top5Artistas, dfArtistasSemanal, dfCancionesSemanal, tiempoSemanal = procesarDatosJson(archivosPrueba)
        
        while True:
            print("\n" + "="*30)
            print("📊 VISOR DE DATOS SPOTIFY 📊")
            print("="*30)
            print("1. Canciones Top 1 (Mensual)")
            print("2. Artistas Top 1 (Mensual)")
            print("3. Resumen Feeling (Mensual)")
            print("4. Tiempo Total (Mensual)")
            print("5. Top 5 Canciones (Mensual)")
            print("6. Top 5 Artistas (Mensual)")
            print("7. Artistas Top 3 (Semanal)")
            print("8. Canciones Top 3 (Semanal)")
            print("9. Tiempo Total (Semanal)")
            print("0. Salir")
            print("="*30)
            
            opcionElegida = input("\nElige el número de la tabla que quieres ver: ")
            
            match opcionElegida:
                case "1":
                    print("\n--- CANCIONES TOP 1 MENSUAL ---")
                    print(cancionesTop1)
                case "2":
                    print("\n--- ARTISTAS TOP 1 MENSUAL ---")
                    print(artistasTop1)
                case "3":
                    print("\n--- RESUMEN FEELING ---")
                    print(resumenFeeling)
                case "4":
                    print("\n--- TIEMPO MENSUAL ---")
                    print(dfTiempoMensual)
                case "5":
                    print("\n--- TOP 5 CANCIONES ---")
                    print(top5Canciones)
                case "6":
                    print("\n--- TOP 5 ARTISTAS ---")
                    print(top5Artistas)
                case "7":
                    print("\n--- ARTISTAS SEMANAL ---")
                    print(dfArtistasSemanal)
                case "8":
                    print("\n--- CANCIONES SEMANAL ---")
                    print(dfCancionesSemanal)
                case "9":
                    print("\n--- TIEMPO SEMANAL ---")
                    print(tiempoSemanal)
                case "0":
                    print("\nCerrando el visor... ¡Buen trabajo!")
                    break
                case _:
                    print("\n Opción no válida. Por favor, elige un número del 0 al 9.")