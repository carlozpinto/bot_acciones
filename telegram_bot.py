import asyncio
import requests
import yfinance as yf
import os
import datetime
import sys  
from telegram import Bot
from dotenv import load_dotenv

# --- CARGA DE CONFIGURACIÓN ---
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
ACCIONES_CONFIG = os.getenv('ACCIONES_CONFIG')
LOL_API_KEY = os.getenv("LOL_SPORTS_TOKEN")

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

# --- FUNCIÓN: OBTENER PARTIDOS DE FÚTBOL ---
def partidos_futbol():
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

# --- FUNCIÓN: OBTENER PARTIDOS DE LOL ESPORTS ---
def obtener_lol():
    
    print(f"DEBUG LOL_API_KEY: {'configurado' if LOL_API_KEY else 'VACÍO'}") 
    
    # Si no hay token configurado, retornamos mensaje de advertencia
    if not LOL_API_KEY:
        return "🎮 *LoL Esports*\n\n⚠️ Token no configurado\n"
    
    url_lol = "https://api.pandascore.co/lol/matches/upcoming"
    
    ahora = datetime.datetime.now(datetime.timezone.utc)
    fin = ahora + datetime.timedelta(hours=24)
    
    parametros = {
        "range[begin_at]": f"{ahora.isoformat()}Z,{fin.isoformat()}Z",
        "sort": "begin_at"
    }
    
    headers = {
        "Authorization": f"Bearer {LOL_API_KEY}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url_lol, params=parametros, headers=headers)
        data = response.json()
        
        ligas = [
            "LCK Challengers League",
            "LCK",
            "LPL",
            "LEC",
            "LCS",
            "CBLOL"
        ]
        
        partidos = {}
        
        # Iteramos sobre los partidos protegiendo contra respuestas inesperadas
        for match in data:
            liga_actual = match["league"]["name"]
            
            if liga_actual in ligas:
                if liga_actual not in partidos:
                    partidos[liga_actual] = []
                    
                partidos[liga_actual].append({
                    "rival1": match["opponents"][0]["opponent"]["name"],
                    "rival2": match["opponents"][1]["opponent"]["name"],
                    "hora": match["begin_at"]
                })
        
        mensaje = "🎮 *Partidos de LoL Esports — próximas 24 horas*\n"
        
        if not partidos:
            mensaje += "😴 No hay partidos en las próximas 24 horas"
        else:
            for liga, partido in partidos.items():
                mensaje += "─" * 30 + "\n"
                mensaje += f"🏆 {liga}\n"
                
                for p in partido:
                    horario = datetime.datetime.strptime(p['hora'], "%Y-%m-%dT%H:%M:%SZ")
                    horario = horario - datetime.timedelta(hours=6)
                    horario = horario.strftime('%I:%M %p')
                    mensaje += f"  ⚔️  {p['rival1']} vs {p['rival2']} | 🕐 {horario}\n"
        
        return mensaje

    except Exception as e:
        # Si la API falla o devuelve algo inesperado, retornamos el error sin detener el bot
        return f"🎮 *LoL Esports*\n\n❌ Error: {str(e)}\n"

# --- FUNCIÓN PRINCIPAL DE EJECUCIÓN (ASÍNCRONA) ---
async def enviar_resumen():
    bot = Bot(token=TOKEN)
    dia_semana = datetime.datetime.now().weekday()
    reporte_futbol = partidos_futbol()
    reporte_lol = obtener_lol()
    
    if dia_semana < 5:
        reporte_acciones = obtener_acciones()
        mensaje_final = f"{reporte_acciones}\n{'─'*15}\n{reporte_futbol}\n{'─'*15}\n{reporte_lol}"
    else:
        mensaje_final = f"🔭 *REPORTE DE FIN DE SEMANA*\n_Mercados cerrados_\n\n{reporte_futbol}\n{'─'*15}\n{reporte_lol}"

    await bot.send_message(
        chat_id=CHAT_ID,
        text=mensaje_final,
        parse_mode="Markdown"
    )
    print(f"🚀 Reporte enviado al Canal (Día de la semana: {dia_semana})")

# --- PUNTO DE ARRANQUE DEL SCRIPT ---
if __name__ == "__main__":
    try:
        asyncio.run(enviar_resumen())
        print("Finalizando ejecución exitosa...")
        sys.exit(0)  
    except Exception as e:
        print(f"❌ Error fatal en la ejecución: {e}")
        sys.exit(1)