import os
import requests
import datetime
from dotenv import load_dotenv

# Cargar configuración local
load_dotenv()

def obtener_reporte_dia_actual():
    api_key = os.getenv('FOOTBALL_API_KEY')
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-apisports-key': api_key}
    
    # Capturamos la fecha exacta de HOY
    hoy = datetime.date.today()
    fecha_str = hoy.strftime('%Y-%m-%d')
    
    # Formatear título dinámico para el mensaje
    fecha_titulo = hoy.strftime('%d/%m/%y')
    
    LIGAS_ELITE = [
        {"n": "Liga MX", "p": "Mexico"},
        {"n": "Liga MX Femenil", "p": "Mexico"},
        {"n": "Liga de Expansión MX", "p": "Mexico"},
        {"n": "Premier League", "p": "England"},
        {"n": "La Liga", "p": "Spain"},
        {"n": "Serie A", "p": "Italy"},
        {"n": "Bundesliga", "p": "Germany"},
        {"n": "Ligue 1", "p": "France"},
        {"n": "UEFA Champions League", "p": "World"},
        {"n": "UEFA Europa League", "p": "World"},
        {"n": "CONCACAF Champions League", "p": "World"},
        {"n": "CONMEBOL Libertadores", "p": "World"},
        {"n": "Friendlies", "p": "World"}
    ]

    print(f"🏟️  **PARTIDOS DE HOY ({fecha_titulo})** 🏟️\n")

    params = {"date": fecha_str, "timezone": "America/Mexico_City"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        partidos = data.get('response', [])
        
        encontrados = 0
        for p in partidos:
            nombre_api = p['league']['name']
            pais_api = p['league']['country']
            
            for liga in LIGAS_ELITE:
                if nombre_api == liga["n"] and (pais_api == liga["p"] or liga["p"] == "World"):
                    encontrados += 1
                    
                    # Limpieza de nombres
                    local = p['teams']['home']['name'].replace(' W', '')
                    visita = p['teams']['away']['name'].replace(' W', '')
                    
                    # Formato 12 Horas
                    hora_24 = p['fixture']['date'].split('T')[1][:5]
                    hora_obj = datetime.datetime.strptime(hora_24, "%H:%M")
                    hora_12 = hora_obj.strftime("%I:%M %p")
                    
                    # Lógica de Marcador y Estado
                    status = p['fixture']['status']['short']
                    goles_l = p['goals']['home']
                    goles_v = p['goals']['away']

                    if status == "NS": # No ha empezado
                        st_icon = "⏰"
                        info_partido = f"**{local}** vs **{visita}**"
                    elif status in ["1H", "2H", "HT"]: # En vivo
                        st_icon = "⚽ En vivo"
                        info_partido = f"**{local}** {goles_l} - {goles_v} **{visita}**"
                    elif status == "FT": # Finalizado
                        st_icon = "🏁 Fin"
                        info_partido = f"**{local}** {goles_l} - {goles_v} **{visita}**"
                    else: # Otros (Cancelado, Postpuesto)
                        st_icon = "⚠️"
                        info_partido = f"**{local}** vs **{visita}** ({status})"

                    print(f"{st_icon} `{hora_12}` | {info_partido}")
                    print(f"   _{nombre_api}_")
        
        if encontrados == 0:
            print("⚽ Sin partidos relevantes para hoy.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    obtener_reporte_dia_actual()