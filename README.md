# 📈 Finanzas, Fútbol & LoL Esports: Bot de Seguimiento Personal

Dashboard interactivo y bot de Telegram diseñado para monitorear activos financieros, la agenda deportiva de élite y partidos de LoL Esports en un solo lugar.

## 🚀 ¿Qué hace este proyecto?

Este sistema actúa como un asistente personal que automatiza la entrega de información crítica cada mañana:

### 💰 Monitoreo de Inversiones
- **Consulta en tiempo real:** Tracking de tickers configurables vía Yahoo Finance.
- **Análisis de Rendimiento:** Cálculo de cambio porcentual diario con indicadores visuales (🟢/🔴).
- **Dashboard Interactivo:** Visualización de historial de 3 meses con medias móviles (20 días) y métricas clave.

### ⚽ Cartelera de Fútbol Elite
- **Filtro Inteligente:** Reporte de partidos exclusivamente de ligas "Top", eliminando el ruido de ligas menores.
- **Estado en tiempo real:** Detección automática de partidos en vivo, finalizados o por iniciar.
- **Formato Humano:** Horarios en formato 12h (CDMX), limpieza de nombres y marcadores en vivo.

### 🎮 LoL Esports
- **Partidos profesionales:** Cobertura de las principales ligas de League of Legends (LCK, LPL, LEC, LCS, CBLOL).
- **Próximas 24 horas:** Muestra todos los partidos del día sin importar zona horaria.
- **Horario CDMX:** Conversión automática de UTC a hora de México.

---

## 🏆 Cobertura de Ligas

### Fútbol
| Región | Competiciones Incluidas |
|--------|------------------------|
| **México** | Liga MX, Liga MX Femenil, Liga de Expansión MX |
| **Europa (Top 5)** | Premier League, La Liga, Serie A, Bundesliga, Ligue 1 |
| **Internacional Clubes** | Champions League, Europa League, Concachampions, Libertadores |
| **Selecciones** | World Cup, Copa América, Eurocopa, Amistosos FIFA |

### LoL Esports
| Liga | Región |
|------|--------|
| LCK | Corea |
| LPL | China |
| LEC | Europa |
| LCS | Norteamérica |
| CBLOL | Brasil |
| LCK Challengers | Corea (Ascenso) |

---

## 🛠️ Tecnologías utilizadas

- **Python 3.9+**
- **yfinance** — Datos financieros en tiempo real
- **API-Sports (Football)** — Motor de datos deportivos globales
- **PandaScore API** — Datos de partidos de LoL Esports
- **Telegram Bot API** — Interfaz de notificaciones
- **GitHub Actions** — Orquestación y ejecución automática 24/7 en la nube
- **Streamlit & Plotly** — Visualización de datos en el dashboard

---

## ▶️ Configuración Local

1. **Clona el repositorio:**
```bash
git clone https://github.com/carlozpinto/bot_personal.git
```

2. **Crea y activa un entorno virtual:**
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate
```

3. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

4. **Variables de Entorno (.env):**
Copia `config.example.py` a `config.py` y edita tus preferencias. Luego crea un archivo `.env`:
```bash
TELEGRAM_TOKEN=tu_token_de_botfather
TELEGRAM_CHAT_ID=tu_id_de_usuario
FOOTBALL_API_KEY=tu_key_de_api_sports
LOL_SPORTS_TOKEN=tu_token_de_pandascore
ACCIONES_CONFIG=BYDDY,NFLX,UNH
```
---

## 🤖 Automatización con GitHub Actions

El bot es **100% autónomo**. Se ejecuta automáticamente de lunes a viernes a las **08:00 AM (Hora CDMX)**.

### 🛡️ Configuración de Secrets

`Settings` > `Secrets and variables` > `Actions` > `New repository secret`

| Secreto | Descripción |
|---------|-------------|
| `TELEGRAM_TOKEN` | Token proporcionado por @BotFather |
| `TELEGRAM_CHAT_ID` | Tu ID numérico de Telegram |
| `FOOTBALL_API_KEY` | Tu llave de API-Sports |
| `LOL_SPORTS_TOKEN` | Tu token de PandaScore |
| `ACCIONES_CONFIG` | Tickers a monitorear (Ej: `BYDDY,NFLX,UNH`) |

---

## 📊 Vista del Proyecto

![Dashboard Preview](dashboard_preview.png)

---

## 👤 Autor

**Carlos Pinto** ✨ [LinkedIn](https://www.linkedin.com/in/carlozpinto) | 🚀 [GitHub](https://github.com/carlozpinto)