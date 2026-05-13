import spotipy
from datetime import datetime

def ticket(token):
    try:
        sp = spotipy.Spotify(auth=token)
        historialCrudo = sp.current_user_recently_played(limit=10)
        perfil = sp.current_user()
        nombreCliente = perfil.get("display_name", "Usuario misterioso")
        cancionesTicket = []
        for item in historialCrudo.get("items",[]):
            track = item.get("track",{})
            duracionMs = track.get("duration_ms", 0) // 1000
            minutos, segundos = divmod(duracionMs, 60)
            fechaCruda = item.get("played_at", "2000-01-01T00:00:00Z")
            fechaLimpia = fechaCruda.replace("Z", "").split(".")[0]
            fechaObj = datetime.strptime(fechaLimpia, "%Y-%m-%dT%H:%M:%S")
            lista_artistas = track.get("artists", [])
            if isinstance(lista_artistas, list) and len(lista_artistas) > 0:
                artista = lista_artistas[0].get("name", "Artista Desconocido")
            else:
                artista = "Artista Desconocido"
            cancionesTicket.append({
                "nombre":track.get("name", "Cancion Desconocida"),
                "artista":artista,
                "duracion":f"{minutos}:{segundos:02d}",
                "fecha":fechaObj.strftime("%d/%m/%Y - %I:%M %p")
            })
        return {
            "canciones": cancionesTicket,
            "nombre": nombreCliente
        }
    except Exception as e:
        print(f"Error en motor Oauth: {e}")
        return None