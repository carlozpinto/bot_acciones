import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Mi Portafolio", page_icon="📈", layout="wide")

st.title("📈 Mi Portafolio de Acciones")
st.caption("Datos en tiempo real via Yahoo Finance")

# Tus acciones
tickers = ["BYDDY", "NFLX", "UNH"]

# Tarjetas de precio actual
st.subheader("Precios actuales")
col1, col2, col3 = st.columns(3)
columnas = [col1, col2, col3]

for i, ticker in enumerate(tickers):
    accion = yf.Ticker(ticker)
    info = accion.fast_info
    cambio_pct = ((info.last_price - info.previous_close) /
                  info.previous_close) * 100
    with columnas[i]:
        st.metric(
            label=ticker,
            value=f"${info.last_price:.2f}",
            delta=f"{cambio_pct:+.2f}%"
        )

# Tabla de resumen últimos 3 meses
st.subheader("Resumen últimos 3 meses")

resumen = []

for ticker in tickers:
    accion = yf.Ticker(ticker)
    historial = accion.history(period="3mo")
    historial.index = historial.index.tz_localize(None)

    precio_actual = historial["Close"].iloc[-1]
    precio_hace_3m = historial["Close"].iloc[0]
    rendimiento = ((precio_actual - precio_hace_3m) / precio_hace_3m) * 100

    resumen.append({
        "Acción": ticker,
        "Precio actual": f"${precio_actual:.2f}",
        "Mínimo 3m": f"${historial['Close'].min():.2f}",
        "Máximo 3m": f"${historial['Close'].max():.2f}",
        "Promedio 3m": f"${historial['Close'].mean():.2f}",
        "Rendimiento 3m": f"{rendimiento:+.2f}%"
    })

df_resumen = pd.DataFrame(resumen)
st.dataframe(df_resumen, use_container_width=True, hide_index=True)

# Sección de alertas
st.subheader("🚨 Alertas del día")

umbral = st.slider("Alertar si cambio diario supera (%):",
                   min_value=1, max_value=10, value=2)

hay_alertas = False

for ticker in tickers:
    accion = yf.Ticker(ticker)
    info = accion.fast_info
    cambio_pct = ((info.last_price - info.previous_close) /
                  info.previous_close) * 100

    if cambio_pct >= umbral:
        st.success(
            f"📈 {ticker} subió {cambio_pct:+.2f}% hoy — por encima de tu umbral de +{umbral}%")
        hay_alertas = True
    elif cambio_pct <= -umbral:
        st.error(
            f"📉 {ticker} bajó {cambio_pct:.2f}% hoy — por debajo de tu umbral de -{umbral}%")
        hay_alertas = True

if not hay_alertas:
    st.info(
        f"✅ Todo tranquilo — ninguna acción superó el {umbral}% de cambio hoy")

# Gráfica histórica
st.subheader("Historial de precios — últimos 3 meses")

ticker_seleccionado = st.selectbox("Selecciona una acción:", tickers)

accion = yf.Ticker(ticker_seleccionado)
historial = accion.history(period="3mo")
historial.index = historial.index.tz_localize(None)

historial["MA20"] = historial["Close"].rolling(window=20).mean()

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=historial.index,
    y=historial["Close"],
    name="Precio cierre",
    line=dict(color="#00BFFF", width=2)
))

fig.add_trace(go.Scatter(
    x=historial.index,
    y=historial["MA20"],
    name="Media móvil 20 días",
    line=dict(color="#FFA500", width=2, dash="dash")
))

fig.update_layout(
    title=f"Precio de cierre — {ticker_seleccionado}",
    xaxis_title="Fecha",
    yaxis_title="Precio (USD)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

st.plotly_chart(fig, use_container_width=True)
