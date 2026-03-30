# Importamos la libreria de Yahoo Finance
import yfinance as yf

# Ponemos algunas acciones de prueba
tickers = ["AMZN", "NFLX", "TSLA"]

# Ciclo for para iterar las acciones
for ticker in tickers:
    
    # Obtenemos el objeto de la accion
    accion = yf.Ticker(ticker)
    
    # Tomamos la info basica
    info = accion.fast_info

    # Agregamos el texto estructurado que saldra en pantalla
    print(f"\n📈 {ticker}")
    print(f"   Precio actual:  ${info.last_price:.2f}")
    print(f"   Precio de ayer: ${info.previous_close:.2f}")
    
    # Al precio actual le restamos el precio de cierre de ayer para sacar porcentaje
    cambio = info.last_price - info.previous_close
    cambio_pct = (cambio / info.previous_close) * 100
    print(f"   Cambio hoy:     {cambio_pct:+.2f}%")

# Hacemos un historial de cada accion
print("\n--- Historial últimos 30 días ---")

for ticker in tickers:
    accion = yf.Ticker(ticker)
    historial = accion.history(period="1mo")
    print(f"\n{ticker}:")
    print(historial[["Close", "Volume"]].tail(5))
