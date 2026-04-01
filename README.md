# 📈 Finanzas & Fútbol: Bot de Seguimiento Personal

Dashboard interactivo y bot de Telegram diseñado para monitorear activos financieros y la agenda deportiva de élite en un solo lugar.

## 🚀 ¿Qué hace este proyecto?

Este sistema actúa como un asistente personal que automatiza la entrega de información crítica cada mañana:

### 💰 Monitoreo de Inversiones
* **Consulta en tiempo real:** Tracking de tickers configurables (**BYDDY, NFLX, UNH**) vía Yahoo Finance.
* **Análisis de Rendimiento:** Cálculo de cambio porcentual diario con indicadores visuales (🟢/🔴).
* **Dashboard Interactivo:** Visualización de historial de 3 meses con medias móviles (20 días) y métricas clave.

### ⚽ Cartelera de Fútbol Elite
* **Filtro Inteligente:** Reporte de partidos exclusivamente de ligas "Top", eliminando el ruido de ligas menores.
* **Detección de Amistosos:** Seguimiento automático de la Selección Mexicana y juegos internacionales FIFA.
* **Formato Humano:** Horarios en formato 12h (CDMX), limpieza de nombres y estados en tiempo real (En vivo/Finalizado).

---

## 🏆 Cobertura de Ligas Elite

El bot filtra automáticamente más de 400 partidos diarios para mostrar solo las competiciones más relevantes:

| Región | Competiciones Incluidas |
| :--- | :--- |
| **México** | Liga MX, Liga MX Femenil, Liga de Expansión MX |
| **Europa (Top 5)** | Premier League, La Liga, Serie A, Bundesliga, Ligue 1 |
| **Internacional Clubes** | Champions League, Europa League, Concachampions, Libertadores |
| **Selecciones** | World Cup, Copa América, Eurocopa, Gold Cup, Nations League |
| **Especiales** | Amistosos Internacionales (FIFA) y Leagues Cup |

---

## 🛠️ Tecnologías utilizadas

* **Python 3.9+**
* **yfinance:** Datos financieros en tiempo real.
* **API-Sports (Football):** Motor de datos deportivos globales.
* **Telegram Bot API:** Interfaz de notificaciones.
* **GitHub Actions:** Orquestación y ejecución automática 24/7 en la nube.
* **Streamlit & Plotly:** Visualización de datos en el dashboard.

---

## ▶️ Configuración Local

1. **Clona el repositorio:**
   ```bash
   git clone [https://github.com/carlozpinto/bot_acciones.git](https://github.com/carlozpinto/bot_acciones.git)

2. **Crea y activa un entorno virtual:**

    ```bash
    python -m v*env venv
    # En Windows:
    venv\Scripts\activate
    # En Mac/Linux:
    source venv/bin/activate

3. **Instala las dependencias:**

    ```bash
    pip install yfinance pandas plotly streamlit requests python-dotenv

4. **Variables de Entorno (.env):**
Crea un archivo .env en la raíz con lo siguiente:

    ```b
    TELEGRAM_TOKEN=tu_token_de_botfather
    TELEGRAM_CHAT_ID=tu_id_de_usuario
    FOOTBALL_API_KEY=tu_key_de_api_sports
    ACCIONES_CONFIG=BYDDY,NFLX,UNH

Gemini dijo
¡Perfecto! Aquí tienes el README.md completo, integrando la tabla de ligas con un formato limpio, profesional y con los saltos de línea necesarios para que se vea impecable en tu perfil de GitHub.

Markdown
# 📈 Finanzas & Fútbol: Bot de Seguimiento Personal

Dashboard interactivo y bot de Telegram diseñado para monitorear activos financieros y la agenda deportiva de élite en un solo lugar.

## 🚀 ¿Qué hace este proyecto?

Este sistema actúa como un asistente personal que automatiza la entrega de información crítica cada mañana:

### 💰 Monitoreo de Inversiones
* **Consulta en tiempo real:** Tracking de tickers configurables (**BYDDY, NFLX, UNH**) vía Yahoo Finance.
* **Análisis de Rendimiento:** Cálculo de cambio porcentual diario con indicadores visuales (🟢/🔴).
* **Dashboard Interactivo:** Visualización de historial de 3 meses con medias móviles (20 días) y métricas clave.

### ⚽ Cartelera de Fútbol Elite
* **Filtro Inteligente:** Reporte de partidos exclusivamente de ligas "Top", eliminando el ruido de ligas menores.
* **Detección de Amistosos:** Seguimiento automático de la Selección Mexicana y juegos internacionales FIFA.
* **Formato Humano:** Horarios en formato 12h (CDMX), limpieza de nombres y estados en tiempo real (En vivo/Finalizado).

---

## 🏆 Cobertura de Ligas Elite

El bot filtra automáticamente más de 400 partidos diarios para mostrar solo las competiciones más relevantes:

| Región | Competiciones Incluidas |
| :--- | :--- |
| **México** | Liga MX, Liga MX Femenil, Liga de Expansión MX |
| **Europa (Top 5)** | Premier League, La Liga, Serie A, Bundesliga, Ligue 1 |
| **Internacional Clubes** | Champions League, Europa League, Concachampions, Libertadores |
| **Selecciones** | World Cup, Copa América, Eurocopa, Gold Cup, Nations League |
| **Especiales** | Amistosos Internacionales (FIFA) y Leagues Cup |

---

## 🛠️ Tecnologías utilizadas

* **Python 3.9+**
* **yfinance:** Datos financieros en tiempo real.
* **API-Sports (Football):** Motor de datos deportivos globales.
* **Telegram Bot API:** Interfaz de notificaciones.
* **GitHub Actions:** Orquestación y ejecución automática 24/7 en la nube.
* **Streamlit & Plotly:** Visualización de datos en el dashboard.

---

## ▶️ Configuración Local

1. **Clona el repositorio:**
   ```bash
   git clone (https://github.com/carlozpinto/bot_acciones.git)
Crea y activa un entorno virtual:

Bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate
Instala las dependencias:

Bash
pip install yfinance pandas plotly streamlit requests python-dotenv
Variables de Entorno (.env):
Crea un archivo .env en la raíz con lo siguiente:

Fragmento de código
TELEGRAM_TOKEN=tu_token_de_botfather
TELEGRAM_CHAT_ID=tu_id_de_usuario
FOOTBALL_API_KEY=tu_key_de_api_sports
ACCIONES_CONFIG=BYDDY,NFLX,UNH
🤖 Automatización (GitHub Actions)
El bot está configurado para ejecutarse automáticamente todos los días (incluyendo fines de semana) a las 07:00 AM (Hora CDMX) mediante GitHub Actions.

Para que funcione en la nube, asegúrate de configurar los Secrets en tu repositorio (Settings > Secrets and variables > Actions):

TELEGRAM_TOKEN

TELEGRAM_CHAT_ID

FOOTBALL_API_KEY

ACCIONES_CONFIG

📊 Vista del Proyecto
👤 Autor
Carlos Pinto

LinkedIn

GitHub