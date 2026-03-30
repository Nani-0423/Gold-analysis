import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from streamlit_lottie import st_lottie
import requests
import time

# --- CONFIG & STYLING ---
st.set_page_config(page_title="Gold Analytics Pro", layout="wide")

# Custom CSS for a "Premium" look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #d4af37; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# Function to load Lottie Animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

# --- DATA ENGINE ---
@st.cache_data(ttl=3600)
def fetch_gold_data():
    tax_factor = 1.092
    gold = yf.download("GC=F", period="2y", interval="1d", progress=False)
    inr = yf.download("INR=X", period="2y", interval="1d", progress=False)
    
    if isinstance(gold.columns, pd.MultiIndex): gold.columns = gold.columns.get_level_values(0)
    if isinstance(inr.columns, pd.MultiIndex): inr.columns = inr.columns.get_level_values(0)

    df = pd.merge(gold[['Close']], inr[['Close']].rename(columns={'Close':'USDINR'}), 
                 left_index=True, right_index=True).dropna()
    df['Price_Gram'] = (df['Close'] / 31.1034768) * df['USDINR'] * tax_factor
    return df

# --- APP LAYOUT ---
lottie_gold = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_f7S68S.json") # Gold coin animation

with st.container():
    col_a, col_b = st.columns([1, 4])
    with col_a:
        st_lottie(lottie_gold, height=120, key="gold_anim")
    with col_b:
        st.title("Gold Premier Prediction Engine")
        st.markdown("_Advanced Machine Learning & Real-time Market Analytics_")

try:
    df = fetch_gold_data()
    current_p = df['Price_Gram'].iloc[-1]
    prev_p = df['Price_Gram'].iloc[-2]
    delta = current_p - prev_p

    # Metrics Row
    m1, m2, m3 = st.columns(3)
    m1.metric("Live Gold (1g)", f"₹{current_p:,.2f}", f"{delta:,.2f} INR")
    m2.metric("USD/INR Rate", f"{df['USDINR'].iloc[-1]:,.2f}")
    m3.metric("Market Sentiment", "Bullish", delta_color="normal")

    # --- MACHINE LEARNING FORECAST ---
    df_m = df.reset_index()
    df_m['Ordinal'] = df_m['Date'].map(pd.Timestamp.toordinal)
    
    # Model Training
    model = LinearRegression().fit(df_m.tail(120)[['Ordinal']], df_m.tail(120)['Price_Gram'])
    
    # Predict 2026
    future_dates = pd.date_range(start="2026-01-01", end="2026-12-01", freq='MS')
    future_ord = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
    preds = model.predict(future_ord)

    # --- RARE ANIMATED CHART (Plotly) ---
    st.subheader("Interactive 2026 Trajectory")
    
    fig = go.Figure()

    # Historical Data Trace
    fig.add_trace(go.Scatter(
        x=df.index[-100:], y=df['Price_Gram'].tail(100),
        name='Historical Price', line=dict(color='#2c3e50', width=2)
    ))

    # Prediction Trace with "Reveal" animation
    fig.add_trace(go.Scatter(
        x=future_dates, y=preds,
        name='2026 Forecast',
        line=dict(color='#d4af37', width=4, dash='dot'),
        marker=dict(size=8, symbol='diamond')
    ))

    fig.update_layout(
        hovermode="x unified",
        template="plotly_white",
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False),
        yaxis=dict(zeroline=False)
    )

    # Adding a slider for the user to explore dates
    fig.update_xaxes(rangeslider_visible=True)

    st.plotly_chart(fig, use_container_width=True)

    # Detailed Table
    with st.expander("View Full 2026 Monthly Breakdown"):
        report = pd.DataFrame({'Month': future_dates.strftime('%B %Y'), 'Predicted Price': preds})
        st.dataframe(report, use_container_width=True)

except Exception as e:
    st.error(f"Waiting for market data connection... {e}")
