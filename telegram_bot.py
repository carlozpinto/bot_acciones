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
    # Verificamos si la variable existe y no está vacía
    if not ACCIONES_CONFIG:
        return "📈 *Portafolio*\n\nNo hay acciones configuradas\n"
    
    # Convertimos el texto "TSLA,NFLX" en una lista
    tickers = [t.strip().upper() for t in ACCIONES_CONFIG.split(',')]

    # Obtenemos la fecha actual para el encabezado
    ahora = datetime.datetime.now().strftime("%d/%m/%Y")
    mensaje = f"📈 *RESUMEN DE MERCADOS* ({ahora})\n\n"

    # Bucle para iterar sobre las acciones (Yahoo Finance)
    for ticker in tickers:
        try:
            accion = yf.Ticker(ticker)
            info = accion.fast_info
            
            # Cálculo de porcentaje de cambio diario
            cambio_pct = ((info.last_price - info.previous_close) / info.previous_close) * 100
            
            # Semáforo visual: Verde para ganancia, Rojo para pérdida
            emoji = "🟢" if cambio_pct >= 0 else "🔴"
            
            mensaje += f"{emoji} *{ticker}*\n"
            mensaje += f"   Precio: `${info.last_price:.2f}`\n"
            mensaje += f"   Cambio: `{cambio_pct:+.2f}%`\n\n"
        except Exception:
            continue # Si una falla, seguimos con la que sigue
            
    mensaje += "💡 _Datos via Yahoo Finance_\n"
    return mensaje

# --- FUNCIÓN PARA OBTENER PARTIDOS DE FUTBOL (API-SPORTS) ---
def obtener_reporte_futbol():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-apisports-key': FOOTBALL_API_KEY}
    
    # Capturamos la fecha de HOY
    hoy = datetime.date.today()
    fecha_str = hoy.strftime('%Y-%m-%d')
    fecha_titulo = hoy.strftime('%d/%m/%y')
    
    # Configuración de Ligas Elite (Filtro Personalizado)
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

    mensaje = f"🏟️ *PARTIDOS DE HOY ({fecha_titulo})* 🏟️\n"
    hay_partidos = False

    # Parámetros para la API (Horario CDMX)
    params = {"date": fecha_str, "timezone": "America/Mexico_City"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        partidos = data.get('response', [])
        
        for p in partidos:
            nombre_api = p['league']['name']
            pais_api = p['league']['country']
            
            for liga in LIGAS_ELITE:
                if nombre_api == liga["n"] and (pais_api == liga["p"] or liga["p"] == "World"):
                    hay_partidos = True
                    
                    # Limpieza de nombres (Adiós a la "W" de Women)
                    local = p['teams']['home']['name'].replace(' W', '')
                    visita = p['teams']['away']['name'].replace(' W', '')
                    
                    # Formato 12 Horas (AM/PM)
                    hora_24 = p['fixture']['date'].split('T')[1][:5]
                    hora_obj = datetime.datetime.strptime(hora_24, "%H:%M")
                    hora_12 = hora_obj.strftime("%I:%M %p")
                    
                    # Lógica de Marcador y Emojis de Estado
                    status = p['fixture']['status']['short']
                    goles_l = p['goals']['home']
                    goles_v = p['goals']['away']

                    if status == "NS": # Por empezar
                        st_icon, info_res = "⏰", f"**{local}** vs **{visita}**"
                    elif status in ["1H", "2H", "HT"]: # En juego
                        st_icon, info_res = "⚽ En vivo", f"**{local}** {goles_l} - {goles_v} **{visita}**"
                    elif status == "FT": # Finalizado
                        st_icon, info_res = "🏁 Fin", f"**{local}** {goles_l} - {goles_v} **{visita}**"
                    else:
                        st_icon, info_res = "⚠️", f"**{local}** vs **{visita}**"

                    mensaje += f"\n{st_icon} `{hora_12}` | {info_res}\n   _{nombre_api}_"

        if not hay_partidos:
            mensaje += "\n⚽ _Sin partidos relevantes para hoy._"

    except Exception as e:
        mensaje += f"\n❌ _Error al consultar fútbol: {str(e)}_"

    return mensaje

# --- FUNCIÓN PRINCIPAL PARA ENVIAR EL RESUMEN ---
async def enviar_resumen():
    bot = Bot(token=TOKEN)
    
    # Obtenemos el día de la semana (0=Lunes, 5=Sábado, 6=Domingo)
    dia_semana = datetime.datetime.now().weekday()
    
    # Generamos el reporte de fútbol (Este sale siempre)
    reporte_futbol = obtener_reporte_futbol()
    
    # Si es Lunes a Viernes (0-4), incluimos las acciones
    if dia_semana < 5:
        reporte_acciones = obtener_acciones()
        mensaje_final = f"{reporte_acciones}\n{'─'*15}\n{reporte_futbol}"
    else:
        # Si es Sábado o Domingo, solo fútbol con nota aclaratoria
        mensaje_final = f"🔭 *REPORTE DE FIN DE SEMANA*\n_Mercados financieros cerrados_\n\n{reporte_futbol}"

    # Enviamos el mensaje al chat configurado
    await bot.send_message(
        chat_id=CHAT_ID,
        text=mensaje_final,
        parse_mode="Markdown"
    )
    print(f"🚀 Mensaje enviado correctamente (Día de la semana: {dia_semana})")

# Punto de entrada del script
if __name__ == "__main__":
    asyncio.run(enviar_resumen())