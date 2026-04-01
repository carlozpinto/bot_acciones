# Agregamos las librerías necesarias
import asyncio
import requests
import yfinance as yf
import os
import datetime
from telegram import Bot
from dotenv import load_dotenv

# Cargamos el .env para obtener las credenciales (Token, ChatID y API Key)
load_dotenv()

# Agregamos las credenciales desde las variables de entorno
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
ACCIONES_CONFIG = os.getenv('ACCIONES_CONFIG')

# --- FUNCIÓN PARA OBTENER LAS ACCIONES ---
def obtener_acciones():
    # Verificamos si la variable existe y no está vacía para evitar errores
    if not ACCIONES_CONFIG:
        return "📈 *Portafolio*\n\nNo hay acciones configuradas\n"
    
    # Convertimos el texto "TSLA,NFLX" en una lista ['TSLA', 'NFLX']
    # .split(',') es el truco para que el bucle for funcione por palabra
    tickers = [t.strip().upper() for t in ACCIONES_CONFIG.split(',')]

    # Obtenemos la fecha actual para el encabezado
    ahora = datetime.datetime.now().strftime("%d/%m/%Y")
    mensaje = f"📈 *RESUMEN DE MERCADOS* ({ahora})\n\n"

    # Bucle for para iterar sobre las acciones y solicitar la info a la API de Yahoo Finance
    for ticker in tickers:
        try:
            # Obtenemos el objeto de la acción en cuestión
            accion = yf.Ticker(ticker)
            # Solicitamos la info básica; precio actual, precio anterior
            info = accion.fast_info
            
            # Al precio actual le restamos el precio de cierre de ayer para sacar el porcentaje
            cambio_pct = ((info.last_price - info.previous_close) / info.previous_close) * 100
            
            # Si el valor es ganancia emoji verde, si es pérdida emoji rojo
            emoji = "🟢" if cambio_pct >= 0 else "🔴"
            
            # Enviamos la info: emoji, ticker, precio con 2 decimales y el cambio
            mensaje += f"{emoji} *{ticker}*\n"
            mensaje += f"   Precio: `${info.last_price:.2f}`\n"
            mensaje += f"   Cambio: `{cambio_pct:+.2f}%`\n\n"
        except Exception:
            # Si una acción falla, que siga con la siguiente y no truene el bot
            continue
            
    mensaje += "💡 _Datos via Yahoo Finance_\n"
    return mensaje

# --- FUNCIÓN PARA OBTENER PARTIDOS DE FUTBOL (API-SPORTS) ---
def obtener_reporte_futbol():
    # URL de la nueva API y headers con nuestra Key
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-apisports-key': FOOTBALL_API_KEY}
    
    # Capturamos la fecha exacta de HOY para que el bot sea diario
    hoy = datetime.date.today()
    fecha_str = hoy.strftime('%Y-%m-%d')
    fecha_titulo = hoy.strftime('%d/%m/%y')
    
    # Lista de Ligas Elite: Filtramos por nombre y país para que no salga basura de otros países
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
        {"n": "Friendlies", "p": "World"} # Amistosos de la Selección
    ]

    # Variable de mensaje inicial
    mensaje = f"🏟️ *PARTIDOS DE HOY ({fecha_titulo})* 🏟️\n"
    hay_partidos = False

    # Parámetros: Solo hoy y con horario de CDMX
    params = {"date": fecha_str, "timezone": "America/Mexico_City"}
    
    try:
        # Hacemos la llamada a la API
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        partidos = data.get('response', [])
        
        # Bucle for para filtrar solo las ligas que nos interesan
        for p in partidos:
            nombre_api = p['league']['name']
            pais_api = p['league']['country']
            
            for liga in LIGAS_ELITE:
                # Doble validación: Nombre de liga y País (o World para torneos internacionales)
                if nombre_api == liga["n"] and (pais_api == liga["p"] or liga["p"] == "World"):
                    hay_partidos = True
                    
                    # Limpieza de nombres: Quitamos el " W" si es femenil para que se vea mejor
                    local = p['teams']['home']['name'].replace(' W', '')
                    visita = p['teams']['away']['name'].replace(' W', '')
                    
                    # Convertimos el horario de la API a formato 12 horas (AM/PM)
                    hora_24 = p['fixture']['date'].split('T')[1][:5]
                    hora_obj = datetime.datetime.strptime(hora_24, "%H:%M")
                    hora_12 = hora_obj.strftime("%I:%M %p")
                    
                    # Checamos el estado del partido para poner marcador o reloj
                    status = p['fixture']['status']['short']
                    goles_l = p['goals']['home']
                    goles_v = p['goals']['away']

                    if status == "NS": # No ha empezado
                        st_icon, info_res = "⏰", f"**{local}** vs **{visita}**"
                    elif status in ["1H", "2H", "HT"]: # En vivo
                        st_icon, info_res = "⚽ En vivo", f"**{local}** {goles_l} - {goles_v} **{visita}**"
                    elif status == "FT": # Finalizado
                        st_icon, info_res = "🏁 Fin", f"**{local}** {goles_l} - {goles_v} **{visita}**"
                    else: # Otros casos (Cancelado/Pospuesto)
                        st_icon, info_res = "⚠️", f"**{local}** vs **{visita}**"

                    # Vamos armando el mensaje partido por partido
                    mensaje += f"\n{st_icon} `{hora_12}` | {info_res}\n   _{nombre_api}_"

        # Si el bucle termina y no encontró nada de nuestras ligas, mandamos mensaje de descanso
        if not hay_partidos:
            mensaje += "\n⚽ _Sin partidos relevantes para hoy._"

    except Exception as e:
        # En caso de error de conexión, lo reportamos en el mensaje
        mensaje += f"\n❌ _Error al consultar fútbol: {str(e)}_"

    return mensaje

# --- FUNCIÓN PRINCIPAL PARA ENVIAR EL RESUMEN ---
async def enviar_resumen():
    # Token de Telegram para levantar el bot
    bot = Bot(token=TOKEN)
    
    # Obtenemos los reportes de ambas funciones
    reporte_acciones = obtener_acciones()
    reporte_futbol = obtener_reporte_futbol()
    
    # Unimos los mensajes con una línea separadora para que se vea ordenado
    mensaje_final = f"{reporte_acciones}\n{'─'*15}\n{reporte_futbol}"

    # Enviamos el mensaje final al ChatID configurado
    await bot.send_message(
        chat_id=CHAT_ID,
        text=mensaje_final,
        parse_mode="Markdown"
    )
    print("🚀 Resumen enviado correctamente a Telegram")

# Ejecutamos el script
if __name__ == "__main__":
    asyncio.run(enviar_resumen())