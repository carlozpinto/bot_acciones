import asyncio
import requests
import yfinance as yf
import os
import datetime
from telegram import Bot
from dotenv import load_dotenv

# 1. CARGA DE CONFIGURACIÓN
# Buscamos el archivo .env para extraer las llaves y tokens de forma segura
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
ACCIONES_CONFIG = os.getenv('ACCIONES_CONFIG')

# --- FUNCIÓN: OBTENER DATOS FINANCIEROS ---
def obtener_acciones():
    # Si el usuario no configuró tickers en el .env, saltamos esta parte
    if not ACCIONES_CONFIG:
        return "📈 *Portafolio*\n\nNo hay acciones configuradas\n"
    
    # Limpiamos los nombres de las acciones (quitamos espacios y pasamos a mayúsculas)
    tickers = [t.strip().upper() for t in ACCIONES_CONFIG.split(',')]
    ahora = datetime.datetime.now().strftime("%d/%m/%Y")
    mensaje = f"📈 *RESUMEN DE MERCADOS* ({ahora})\n\n"

    for ticker in tickers:
        try:
            # Consultamos Yahoo Finance para cada ticket
            accion = yf.Ticker(ticker)
            info = accion.fast_info
            
            # Calculamos la variación porcentual del día
            cambio_pct = ((info.last_price - info.previous_close) / info.previous_close) * 100
            
            # Asignamos color según el rendimiento
            emoji = "🟢" if cambio_pct >= 0 else "🔴"
            
            mensaje += f"{emoji} *{ticker}*\n"
            mensaje += f"   Precio: `${info.last_price:.2f}`\n"
            mensaje += f"   Cambio: `{cambio_pct:+.2f}%`\n\n"
        except Exception:
            # Si una acción falla (ej. ticker mal escrito), continuamos con la siguiente
            continue
            
    mensaje += "💡 _Datos via Yahoo Finance_\n"
    return mensaje

# --- FUNCIÓN: OBTENER PARTIDOS (AGRUPADOS POR LIGA) ---
def obtener_reporte_futbol():
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {'x-apisports-key': FOOTBALL_API_KEY}
    
    hoy = datetime.date.today()
    fecha_str = hoy.strftime('%Y-%m-%d')
    fecha_titulo = hoy.strftime('%d/%m/%y')
    
    # Filtro de ligas que nos interesan para evitar el "ruido" de ligas menores
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

    # Pedimos los partidos en horario de CDMX
    params = {"date": fecha_str, "timezone": "America/Mexico_City"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        partidos = data.get('response', [])
        
        # Diccionario auxiliar para agrupar: {'Liga MX': [partido1, partido2], ...}
        partidos_por_liga = {}

        for p in partidos:
            nombre_api = p['league']['name']
            pais_api = p['league']['country']
            
            for liga in LIGAS_ELITE:
                # Si el partido coincide con nuestra lista elite, lo guardamos
                if nombre_api == liga["n"] and (pais_api == liga["p"] or liga["p"] == "World"):
                    if nombre_api not in partidos_por_liga:
                        partidos_por_liga[nombre_api] = []
                    partidos_por_liga[nombre_api].append(p)

        # Si después del filtro no hay nada interesante hoy
        if not partidos_por_liga:
            return f"🏟️ *PARTIDOS DE HOY ({fecha_titulo})*\n\n⚽ _Sin partidos relevantes para hoy._"

        mensaje = f"🏟️ *PARTIDOS DE HOY ({fecha_titulo})* 🏟️\n"
        
        # Construimos el mensaje liga por liga
        for nombre_liga, lista_partidos in partidos_por_liga.items():
            mensaje += f"\n🏆 *{nombre_liga.upper()}*" 
            
            for p in lista_partidos:
                # Limpiamos nombres de equipos femeniles para que no se vea la "W"
                local = p['teams']['home']['name'].replace(' W', '')
                visita = p['teams']['away']['name'].replace(' W', '')
                
                # Convertimos la hora de la API a formato 12h (AM/PM)
                hora_24 = p['fixture']['date'].split('T')[1][:5]
                hora_obj = datetime.datetime.strptime(hora_24, "%H:%M")
                hora_12 = hora_obj.strftime("%I:%M %p")
                
                status = p['fixture']['status']['short']
                goles_l = p['goals']['home']
                goles_v = p['goals']['away']

                # Definimos el icono y el texto según si ya empezó, está en vivo o terminó
                if status == "NS": # Not Started
                    st_icon, info_res = "⏰", f"{local} vs {visita}"
                elif status in ["1H", "2H", "HT"]: # In Play
                    st_icon, info_res = "⚽ En vivo", f"{local} *{goles_l} - {goles_v}* {visita}"
                else: # Finished / FT
                    st_icon, info_res = "🏁 Fin", f"{local} *{goles_l} - {goles_v}* {visita}"

                mensaje += f"\n{st_icon} `{hora_12}` | {info_res}"
            
            mensaje += "\n" 

        return mensaje

    except Exception as e:
        return f"\n❌ _Error al consultar fútbol: {str(e)}_"

# --- FUNCIÓN PRINCIPAL DE EJECUCIÓN ---
async def enviar_resumen():
    bot = Bot(token=TOKEN)
    
    # 0 = Lunes, ..., 5 = Sábado, 6 = Domingo
    dia_semana = datetime.datetime.now().weekday()
    
    # El reporte de fútbol se genera siempre (7 días a la semana)
    reporte_futbol = obtener_reporte_futbol()
    
    # Lógica de fin de semana: Lunes a Viernes (0 al 4) incluimos la bolsa
    if dia_semana < 5:
        reporte_acciones = obtener_acciones()
        mensaje_final = f"{reporte_acciones}\n{'─'*15}\n{reporte_futbol}"
    else:
        # Sábado y Domingo evitamos la consulta a Yahoo Finance
        mensaje_final = f"🔭 *REPORTE DE FIN DE SEMANA*\n_Mercados financieros cerrados_\n\n{reporte_futbol}"

    # Enviamos el mensaje final al Canal de Telegram
    await bot.send_message(
        chat_id=CHAT_ID,
        text=mensaje_final,
        parse_mode="Markdown"
    )
    print(f"🚀 Reporte enviado al Canal (Día de la semana: {dia_semana})")

# PUNTO DE ARRANQUE
if __name__ == "__main__":
    asyncio.run(enviar_resumen())