# Importamos las librerias a utilizar; REQUESTS para llamar APIS, OS para interactuar con el sistema operativo y DOTENV es para leer los tokens de .env
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Cargamos el .env
load_dotenv()

# Agregamos la fecha actual
ahora = datetime.now().strftime("%d/%m/%Y %H:%M")

# Agregamos la API de football-data.org
API = os.getenv("FOOTBALL_API_KEY")

# Hacemos la llamada a la API
url = 'https://api.football-data.org/v4/matches'
headers = {'X-Auth-Token': API}

# Creamos una variable para guardar la respuesta de la API
response = requests.get(url, headers=headers)

# Convertimos la respuesta a json
data = response.json()

# Imprimimos la fecha
print(f"Los partidos de hoy {ahora} son: ")

# Creamos un diccionario vacio donde albergaremos las ligas
ligas = {}

# Bucle for para iterar sobre las ligas
for partido in data["matches"]:
    liga = partido["competition"]["name"]

    # Si la liga no existe, la crea
    if liga not in ligas:
        ligas[liga] = []

    # Agregamos el nombre del equipo local, visitante y fecha
    ligas[liga].append({
        "local": partido["homeTeam"]["name"],
        "visitante": partido["awayTeam"]["name"],
        "hora": partido["utcDate"]
    })

# Bucle para imprimir los partidos y horarios
for clave, valor in ligas.items():
    print(f"------------ {clave} ------------")
    for partidos in valor:
        horario = datetime.strptime(partidos['hora'], "%Y-%m-%dT%H:%M:%SZ")
        horario = horario - timedelta(hours=6)
        horario = horario.strftime('%I:%M %p')
        print(
            f"🏠 {partidos['local']} vs {partidos['visitante']}✈️  | {horario}")
