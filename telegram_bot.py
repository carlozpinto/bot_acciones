# Agregamos las librerias
import asyncio
import requests
import yfinance as yf
import os
from config import acciones_config, ligas_config
from telegram import Bot
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargamos el .env para obtener las credenciales
load_dotenv()

# Agregamos las credenciales
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
API = os.getenv("FOOTBALL_API_KEY")

# Creamos la funcion para obtener las acciones


def obtener_acciones():
    # Las acciones que queremos, podrian agregarse mas si se requiere
    tickers = acciones_config
    
    #! Verificamos si hay acciones registradas
    if not tickers:
        return "📈 *Portafolio*\n\nNo hay acciones configuradas\n"

    # Obtenemos la fecha actual
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Creamos la variable mensaje que enviaremos
    mensaje = f"📈 *Resumen de tu portafolio*\n_{ahora}_\n\n"

    # Bucle for para iterar sobre las acciones y solicitar la info a la API de Yahoo Finance
    for ticker in tickers:

        # Obtenemos el objeto de la accion en cuestion
        accion = yf.Ticker(ticker)

        # Solicitamos la info basica; precio actual, precio anterior, volumen
        info = accion.fast_info

        # Al precio actual le restamos el precio de cierre de ayer, lo convertimos a proporcion y lo multiplicamos para convertir a porcentaje
        cambio_pct = ((info.last_price - info.previous_close) /
                      info.previous_close) * 100

        # Si el valor dado es mayor a 0, fue ganancia entonces emoji verde, si es menor a 0 es perdida, entonces emoji rojo
        if cambio_pct >= 0:
            emoji = "🟢"
        else:
            emoji = "🔴"

        # Enviamos la info, el emoji y accion en cuestion, precio y el cambio
        mensaje += f"{emoji} *{ticker}*\n"
        mensaje += f"   Precio: ${info.last_price:.2f}\n"
        mensaje += f"   Cambio: {cambio_pct:+.2f}%\n\n"
    mensaje += "💡 _Datos via Yahoo Finance_"

    return mensaje


# Funcion de partidos de futbol
def obtener_partidos():
    # Hacemos la llamada a la API
    url = 'https://api.football-data.org/v4/matches'
    headers = {'X-Auth-Token': API}

    # Creamos una variable para guardar la respuesta de la API
    response = requests.get(url, headers=headers)

    # Convertimos la respuesta a json
    data = response.json()

    # Creamos un diccionario vacio donde albergaremos las ligas
    ligas = {}

    # Bucle for para iterar sobre las ligas
    for partido in data["matches"]:
        liga = partido["competition"]["name"]

        # Si la liga no está en config, la ignoramos
        if liga not in ligas_config:
            continue

        # Si la liga no existe, la crea
        if liga not in ligas:
            ligas[liga] = []

        # Agregamos el nombre del equipo local, visitante y fecha
        ligas[liga].append({
            "local": partido["homeTeam"]["name"],
            "visitante": partido["awayTeam"]["name"],
            "hora": partido["utcDate"]
        })

    # Variable a retornar
    mensaje = "⚽ *Partidos de hoy*\n\n"

    # Bucle para imprimir los partidos y horarios
    for clave, valor in ligas.items():
        mensaje += (f"------------ {clave} ------------\n")
        for partidos in valor:
            horario = datetime.strptime(partidos['hora'], "%Y-%m-%dT%H:%M:%SZ")
            horario = horario - timedelta(hours=6)
            horario = horario.strftime('%I:%M %p')
            mensaje += (f"🏠 {partidos['local']} vs {partidos['visitante']}✈️  | {horario}\n")
            
    # Verificamos si hay partidos, si no hay entonces mandamos mensaje sad        
    if not ligas:
        mensaje = "😴 *Sin partidos hoy* — Disfruta el día libre\n"

    return mensaje

# Creamos funcion para enviar el mensaje
async def enviar_resumen():

    # Token de telegram
    bot = Bot(token=TOKEN)

    # Unimos los mensajes de ambas funciones
    acciones = obtener_acciones()
    partidos = obtener_partidos()
    mensaje = acciones + "\n──────────────\n" + partidos

    await bot.send_message(
        chat_id=CHAT_ID,
        text=mensaje,
        parse_mode="Markdown"
    )

    print("Mensaje enviado correctamente")


asyncio.run(enviar_resumen())
