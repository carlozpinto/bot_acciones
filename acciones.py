# Importamos la libreria de Yahoo Finance
import yfinance as yf

# Mis 3 acciones
tickers = ["BYDDY", "NFLX", "UNH"]

for ticker in tickers:
    accion = yf.Ticker(ticker)
    info = accion.fast_info

    print(f"\n📈 {ticker}")
    print(f"   Precio actual:  ${info.last_price:.2f}")
    print(f"   Precio de ayer: ${info.previous_close:.2f}")
    cambio = info.last_price - info.previous_close
    cambio_pct = (cambio / info.previous_close) * 100
    print(f"   Cambio hoy:     {cambio_pct:+.2f}%")

print("\n--- Historial últimos 30 días ---")

for ticker in tickers:
    accion = yf.Ticker(ticker)
    historial = accion.history(period="1mo")
    print(f"\n{ticker}:")
    print(historial[["Close", "Volume"]].tail(5))
