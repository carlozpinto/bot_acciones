import asyncio
from telegram import Bot
import yfinance as yf
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))


async def enviar_resumen():
    bot = Bot(token=TOKEN)

    tickers = ["BYDDY", "NFLX", "UNH"]

    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
    mensaje = f"📈 *Resumen de tu portafolio*\n_{ahora}_\n\n"

    for ticker in tickers:
        accion = yf.Ticker(ticker)
        info = accion.fast_info
        cambio_pct = ((info.last_price - info.previous_close) /
                      info.previous_close) * 100

        if cambio_pct >= 0:
            emoji = "🟢"
        else:
            emoji = "🔴"

        mensaje += f"{emoji} *{ticker}*\n"
        mensaje += f"   Precio: ${info.last_price:.2f}\n"
        mensaje += f"   Cambio: {cambio_pct:+.2f}%\n\n"

    mensaje += "💡 _Datos via Yahoo Finance_"

    await bot.send_message(
        chat_id=CHAT_ID,
        text=mensaje,
        parse_mode="Markdown"
    )

    print("Mensaje enviado correctamente")

asyncio.run(enviar_resumen())
