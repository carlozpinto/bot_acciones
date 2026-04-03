import asyncio
import requests
import yfinance as yf
import os
import datetime
import sys  # <--- AGREGADO: Necesario para la salida limpia
from telegram import Bot
from dotenv import load_dotenv

# 1. CARGA DE CONFIGURACIÓN
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
ACCIONES_CONFIG = os.getenv('ACCIONES_CONFIG')

# --- FUNCIÓN: OBTENER DATOS FINANCIEROS ---
def obtener_acciones():
    if not ACCIONES_CONFIG:
        return "📈 *Portafolio*\n\nNo hay acciones configuradas\n"
    
    tickers = [t.strip().upper() for t in ACCIONES_CONFIG.split(',')]
    ahora = datetime.datetime.now().strftime("%d/%m/%Y")
    mensaje = f"📈 *RESUMEN DE MERCADOS* ({ahora})\n\n"

    for ticker in tickers:
        try:
            accion = yf.Ticker(ticker)
            info = accion.fast_info
            
            cambio_pct = ((info.last_price - info.previous_close) / info.previous_close) * 100
            emoji = "🟢" if cambio_pct >= 0 else "🔴"
            
            mensaje += f"{emoji} *{ticker}*\n"
            mensaje += f"   Precio: `${info.last_price:.2f}`\n"
            mensaje += f"   Cambio: `{cambio_pct:+.2f}%`\n\n"
        except Exception:
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

    params = {"date": fecha_str, "timezone": "America/Mexico_City"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        partidos = data.get('response', [])
        
        partidos_por_liga = {}

        for p in partidos:
            nombre_api = p['league']['name']
            pais_api = p['league']['country']
            
            for liga in LIGAS_ELITE:
                if nombre_api == liga["n"] and (pais_api == liga["p"] or liga["p"] == "World"):
                    if nombre_api not in partidos_por_liga:
                        partidos_por_liga[nombre_api] = []
                    partidos_por_liga[nombre_api].append(p)

        if not partidos_por_liga:
            return f"🏟️ *PARTIDOS DE HOY ({fecha_titulo})*\n\n⚽ _Sin partidos relevantes para hoy._"

        mensaje = f"🏟️ *PARTIDOS DE HOY ({fecha_titulo})* 🏟️\n"
        
        for nombre_liga, lista_partidos in partidos_por_liga.items():
            mensaje += f"\n🏆 *{nombre_liga.upper()}*" 
            
            for p in lista_partidos:
                local = p['teams']['home']['name'].replace(' W', '')
                visita = p['teams']['away']['name'].replace(' W', '')
                
                hora_24 = p['fixture']['date'].split('T')[1][:5]
                hora_obj = datetime.datetime.strptime(hora_24, "%H:%M")
                hora_12 = hora_obj.strftime("%I:%M %p")
                
                status = p['fixture']['status']['short']
                goles_l = p['goals']['home']
                goles_v = p['goals']['away']

                if status == "NS":
                    st_icon, info_res = "⏰", f"{local} vs {visita}"
                elif status in ["1H", "2H", "HT"]:
                    st_icon, info_res = "⚽ En vivo", f"{local} *{goles_l} - {goles_v}* {visita}"
                else:
                    st_icon, info_res = "🏁 Fin", f"{local} *{goles_l} - {goles_v}* {visita}"

                mensaje += f"\n{st_icon} `{hora_12}` | {info_res}"
            
            mensaje += "\n" 

        return mensaje

    except Exception as e:
        return f"\n❌ _Error al consultar fútbol: {str(e)}_"

# --- FUNCIÓN PRINCIPAL DE EJECUCIÓN ---
async def enviar_resumen():
    bot = Bot(token=TOKEN)
    dia_semana = datetime.datetime.now().weekday()
    reporte_futbol = obtener_reporte_futbol()
    
    if dia_semana < 5:
        reporte_acciones = obtener_acciones()
        mensaje_final = f"{reporte_acciones}\n{'─'*15}\n{reporte_futbol}"
    else:
        mensaje_final = f"🔭 *REPORTE DE FIN DE SEMANA*\n_Mercados financieros cerrados_\n\n{reporte_futbol}"

    await bot.send_message(
        chat_id=CHAT_ID,
        text=mensaje_final,
        parse_mode="Markdown"
    )
    print(f"🚀 Reporte enviado al Canal (Día de la semana: {dia_semana})")

# PUNTO DE ARRANQUE
if __name__ == "__main__":
    try:
        asyncio.run(enviar_resumen())
        # --- EL FIX PARA GITHUB ACTIONS ---
        print("Finalizando ejecución exitosa...")
        sys.exit(0)  # Le dice a GitHub que todo terminó OK
    except Exception as e:
        print(f"❌ Error fatal en la ejecución: {e}")
        sys.exit(1)  # Si algo explota, le dice a GitHub que falló