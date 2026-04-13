# Importamos las librerías necesarias
import datetime
import os
import requests
from dotenv import load_dotenv

# Cargamos las variables de entorno del archivo .env
load_dotenv()

# Token de autenticación y URL base de la API de PandaScore
TOKEN = os.getenv("LOL_SPORTS_TOKEN")
URL = "https://api.pandascore.co/lol/matches/upcoming"

# Obtenemos la hora actual en UTC y calculamos 24 horas después
# Así obtenemos todos los partidos del día sin importar la zona horaria
ahora = datetime.datetime.now(datetime.UTC)
fin = ahora + datetime.timedelta(hours=24)

# Parámetros del request — filtramos por rango de fechas y ordenamos por hora de inicio
parametros = {
    "range[begin_at]": f"{ahora.isoformat()}Z,{fin.isoformat()}Z",
    "sort": "begin_at"
}

# Headers requeridos por la API para autenticación
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

# Hacemos el request a la API y convertimos la respuesta a JSON
response = requests.get(URL, params=parametros, headers=headers)
data = response.json()

# Ligas de LoL Esports que queremos monitorear
# Puedes agregar o quitar ligas según tus preferencias
ligas = [
    "LCK Challengers League",
    "LEC",
    "CBLOL",
    "LCK",
    "LPL",
    "LCS"
]

# Diccionario vacío donde agruparemos los partidos por liga
partidos = {}

# Iteramos sobre todos los partidos de la respuesta
for match in data:
    # Obtenemos el nombre de la liga del partido actual
    liga_actual = match["league"]["name"]

    # Solo procesamos las ligas que están en nuestra lista
    if liga_actual in ligas:

        # Si la liga no existe en el diccionario, la creamos con lista vacía
        if liga_actual not in partidos:
            partidos[liga_actual] = []

        # Agregamos el partido con sus datos al diccionario
        partidos[liga_actual].append({
            "rival1": match["opponents"][0]["opponent"]["name"],
            "rival2": match["opponents"][1]["opponent"]["name"],
            "hora": match["begin_at"]
        })

# Imprimimos los resultados agrupados por liga con formato
print("🎮 *Partidos de LoL Esports — próximas 24 horas*\n")

# Verificamos si hay partidos, si no avisamos
if not partidos:
    print("😴 No hay partidos en las próximas 24 horas")
else:
    for liga, partido in partidos.items():
        print(f"🏆 {liga}")
        print("─" * 30)
        for p in partido:
            # Convertimos la hora UTC a hora México (UTC-6)
            horario = datetime.datetime.strptime(p['hora'], "%Y-%m-%dT%H:%M:%SZ")
            horario = horario - datetime.timedelta(hours=6)
            horario = horario.strftime('%I:%M %p')
            print(f"  ⚔️  {p['rival1']} vs {p['rival2']} | 🕐 {horario}")
        print()