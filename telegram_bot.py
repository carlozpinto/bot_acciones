import asyncio
import requests
import yfinance as yf
import os
import datetime
import sys  
from telegram import Bot
from dotenv import load_dotenv

# --- CARGA DE CONFIGURACIÓN ---
# Buscamos el archivo .env para extraer las llaves y tokens de forma segura
load_dotenv()

# Asignamos las variables de entorno a constantes para usarlas en el script
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
ACCIONES_CONFIG = os.getenv('ACCIONES_CONFIG')
LOL_API_KEY = os.getenv("LOL_SPORTS_TOKEN")

# --- FUNCIÓN: OBTENER DATOS FINANCIEROS ---
def obtener_acciones():
    # Si el usuario no configuró tickers en el .env, saltamos esta parte
    if not ACCIONES_CONFIG:
        return "📈 *Portafolio*\n\nNo hay acciones configuradas\n"
    
    # Limpiamos los nombres de las acciones (quitamos espacios y pasamos a mayúsculas)
    tickers = [t.strip().upper() for t in ACCIONES_CONFIG.split(',')]
    # Obtenemos la fecha actual para el encabezado del mensaje
    ahora = datetime.datetime.now().strftime("%d/%m/%Y")
    mensaje = f"📈 *RESUMEN DE MERCADOS* ({ahora})\n\n"

    # Iteramos sobre cada ticker configurado
    for ticker in tickers:
        try:
            # Consultamos Yahoo Finance para obtener datos rápidos del mercado
            accion = yf.Ticker(ticker)
            info = accion.fast_info
            
            # Calculamos la variación porcentual del día basándonos en el cierre previo
            cambio_pct = ((info.last_price - info.previous_close) / info.previous_close) * 100
            # Asignamos un emoji visual según si la acción subió o bajó
            emoji = "🟢" if cambio_pct >= 0 else "🔴"
            
            # Construimos la línea de texto para esta acción específica
            mensaje += f"{emoji} *{ticker}*\n"
            mensaje += f"   Precio: `${info.last_price:.2f}`\n"
            mensaje += f"   Cambio: `{cambio_pct:+.2f}%`\n\n"
        except Exception:
            # Si una acción falla (ej. ticker mal escrito), continuamos con la siguiente sin detener el bot
            continue
            
    mensaje += "💡 _Datos via Yahoo Finance_\n"
    return mensaje

# --- FUNCIÓN: OBTENER PARTIDOS (AGRUPADOS POR LIGA) ---
def partidos_futbol():
    # URL del endpoint de fixtures de la API de Football-Sports
    url = "https://v3.football.api-sports.io/fixtures"
    # Cabeceras necesarias para la autenticación con API Key
    headers = {'x-apisports-key': FOOTBALL_API_KEY}
    
    # Obtenemos la fecha de hoy en formato año-mes-día para la consulta
    hoy = datetime.date.today()
    fecha_str = hoy.strftime('%Y-%m-%d')
    fecha_titulo = hoy.strftime('%d/%m/%y')
    
    # Lista de ligas "Elite" que queremos filtrar para no saturar el mensaje
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

    # Parámetros de la consulta: fecha de hoy y zona horaria de CDMX
    params = {"date": fecha_str, "timezone": "America/Mexico_City"}
    
    try:
        # Realizamos la petición GET a la API
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        # Extraemos la lista de partidos de la respuesta
        partidos = data.get('response', [])
        
        # Diccionario para agrupar partidos por el nombre de su liga
        partidos_por_liga = {}

        # Clasificamos cada partido recibido según nuestra lista de LIGAS_ELITE
        for p in partidos:
            nombre_api = p['league']['name']
            pais_api = p['league']['country']
            
            for liga in LIGAS_ELITE:
                # Validamos que el nombre y país coincidan (o que sea de categoría 'World')
                if nombre_api == liga["n"] and (pais_api == liga["p"] or liga["p"] == "World"):
                    if nombre_api not in partidos_por_liga:
                        partidos_por_liga[nombre_api] = []
                    partidos_por_liga[nombre_api].append(p)

        # Si tras el filtrado no hay partidos interesantes hoy
        if not partidos_por_liga:
            return f"🏟️ *PARTIDOS DE HOY ({fecha_titulo})*\n\n⚽ _Sin partidos relevantes para hoy._"

        mensaje = f"🏟️ *PARTIDOS DE HOY ({fecha_titulo})* 🏟️\n"
        
        # Construimos el cuerpo del mensaje iterando sobre las ligas agrupadas
        for nombre_liga, lista_partidos in partidos_por_liga.items():
            mensaje += f"\n🏆 *{nombre_liga.upper()}*" 
            
            for p in lista_partidos:
                # Limpiamos nombres de equipos (quitamos la 'W' de equipos femeniles para estética)
                local = p['teams']['home']['name'].replace(' W', '')
                visita = p['teams']['away']['name'].replace(' W', '')
                
                # Formateamos la hora: de formato ISO a formato 12 horas (AM/PM)
                hora_24 = p['fixture']['date'].split('T')[1][:5]
                hora_obj = datetime.datetime.strptime(hora_24, "%H:%M")
                hora_12 = hora_obj.strftime("%I:%M %p")
                
                # Obtenemos el estado del partido y los goles actuales
                status = p['fixture']['status']['short']
                goles_l = p['goals']['home']
                goles_v = p['goals']['away']

                # Lógica de iconos según el estado del encuentro
                if status == "NS": # No empezado
                    st_icon, info_res = "⏰", f"{local} vs {visita}"
                elif status in ["1H", "2H", "HT"]: # En juego o medio tiempo
                    st_icon, info_res = "⚽ En vivo", f"{local} *{goles_l} - {goles_v}* {visita}"
                else: # Finalizado u otros estados de cierre
                    st_icon, info_res = "🏁 Fin", f"{local} *{goles_l} - {goles_v}* {visita}"

                mensaje += f"\n{st_icon} `{hora_12}` | {info_res}"
            
            mensaje += "\n" 

        return mensaje

    except Exception as e:
        # En caso de error en la API, devolvemos un mensaje de error formateado
        return f"\n❌ _Error al consultar fútbol: {str(e)}_"

def obtener_lol():
    # URL del endpoint de la API de rito
    url_lol = "https://api.pandascore.co/lol/matches/upcoming"
    
    # Obtenemos la hora actual UTC y calculamos 24 horas despues
    ahora = datetime.datetime.now(datetime.UTC)
    fin = ahora + datetime.timedelta(hours=24)
    
    # Parametros del request - filtramos por rango de fechas y ordenamos por hora de inicio
    parametros = {
        "range[begin_at]": f"{ahora.isoformat()}Z,{fin.isoformat()}Z",
        "sort": "begin_at"
    }
    
    # Headers requeridos por la API para autenticacion
    headers = {
        "Authorization": f"Bearer {LOL_API_KEY}",
        "Accept": "application/json"
    }
    
    # Hacemos el request a la API y convertimos la respuesta a JSON
    response = requests.get(url_lol, params=parametros, headers=headers)
    data = response.json()
    
    #Ligas de Lol Esports que queremos monitorear
    # Puedes agregar o quitar ligas segun tus preferencias
    ligas = [
        "LCK Challengers League",
        "LCK",
        "LPL",
        "LEC",
        "LCS",
        "CBLOL"
    ]
    
    # Diccionario vacio donde agruparemos los partidos por liga
    partidos = {}
    
    # Iteramos sobre todoso los partidos de la respuesta obtenidos en data
    for match in data:
        # Obtenemos el nombre de la liga del partido actual
        liga_actual = match["league"]["name"]
        
        # Procesamos las ligas que estan en nuestra lista
        if liga_actual in ligas:
            # SI la liga no existe en el diccionario, la creamos con lista vacia
            if liga_actual not in partidos:
                partidos[liga_actual] = []
                
            # Agregamos el partido con sus datos al diccionario
            partidos[liga_actual].append({
                "rival1": match["opponents"][0]["opponent"]["name"],
                "rival2": match["opponents"][1]["opponent"]["name"],
                "hora": match["begin_at"]
            })
    
    # Imprimimos los resultados agrupados por liga con formato 
    mensaje = ("🎮 *Partidos de LoL Esports — próximas 24 horas*\n")
    
    # Verificamos si hay partidos, si no avisamos
    if not partidos:
        mensaje += ("😴 No hay partidos en las próximas 24 horas")
    else:
        for liga, partido in partidos.items():
            mensaje += "─" * 30 + "\n"
            mensaje += f"🏆 {liga}\n"
            
            for p in partido:
            # Convertimos la hora UTC a hora México (UTC-6)
                horario = datetime.datetime.strptime(p['hora'], "%Y-%m-%dT%H:%M:%SZ")
                horario = horario - datetime.timedelta(hours=6)
                horario = horario.strftime('%I:%M %p')
                mensaje += f"  ⚔️  {p['rival1']} vs {p['rival2']} | 🕐 {horario}\n"
                
    return mensaje
    

# --- FUNCIÓN PRINCIPAL DE EJECUCIÓN (ASÍNCRONA) ---
async def enviar_resumen():
    # Inicializamos el objeto del bot de Telegram con el token
    bot = Bot(token=TOKEN)
    # Obtenemos el número del día de la semana (0=Lunes, 6=Domingo)
    dia_semana = datetime.datetime.now().weekday()
    # Generamos el reporte de fútbol
    reporte_futbol = partidos_futbol()
    # Generamos el reporte de lol
    reporte_lol =obtener_lol()
    
    # Lógica de contenido según el día: Lunes a Viernes incluimos Bolsa
    if dia_semana < 5:
        reporte_acciones = obtener_acciones()
        mensaje_final = f"{reporte_acciones}\n{'─'*15}\n{reporte_futbol}\n{'─'*15}\n{reporte_lol}"
    else:
        # Fines de semana omitimos la bolsa ya que los mercados están cerrados
        mensaje_final = f"🔭 *REPORTE DE FIN DE SEMANA*\n_Mercados cerrados_\n\n{reporte_futbol}\n{'─'*15}\n{reporte_lol}"

    # Enviamos el mensaje final al chat o canal configurado
    await bot.send_message(
        chat_id=CHAT_ID,
        text=mensaje_final,
        parse_mode="Markdown"
    )
    print(f"🚀 Reporte enviado al Canal (Día de la semana: {dia_semana})")

# --- PUNTO DE ARRANQUE DEL SCRIPT ---
if __name__ == "__main__":
    try:
        # Ejecutamos la función asíncrona principal
        asyncio.run(enviar_resumen())
        # --- EL FIX PARA GITHUB ACTIONS ---
        # Imprimimos confirmación y cerramos con código 0 para indicar éxito total
        print("Finalizando ejecución exitosa...")
        sys.exit(0)  
    except Exception as e:
        # Si algo falla de forma crítica, imprimimos el error y cerramos con código 1 (Error)
        print(f"❌ Error fatal en la ejecución: {e}")
        sys.exit(1)