import streamlit as st
import plotly.graph_objects as go
from backend.engine import get_market_data, run_forecast
from frontend.assets import load_lottie, inject_rare_ui, st_lottie

st.set_page_config(page_title="AURUM TERMINAL", layout="wide")
inject_rare_ui()

# 1. Loading Animation
lottie_url = "https://assets5.lottiefiles.com/packages/lf20_f7S68S.json"
load_anim = load_lottie(lottie_url)

placeholder = st.empty()
with placeholder.container():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st_lottie(load_anim, height=200)
    st.markdown("<h2 style='text-align:center;'>Accessing Gold Markets...</h2>", unsafe_allow_html=True)

# 2. Logic Execution
try:
    df = get_market_data()
    future_dates, predictions = run_forecast(df)
    placeholder.empty()

    # 3. Main UI
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    st.title("🏆 AURUM GOLD TERMINAL")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="glass-card"><h4>Live Price</h4><h2>₹{df["Price_Gram"].iloc[-1]:,.2f}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="glass-card"><h4>USD/INR</h4><h2>₹{df["USDINR"].iloc[-1]:.2f}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="glass-card"><h4>Dec 2026 Target</h4><h2>₹{predictions[-1]:,.2f}</h2></div>', unsafe_allow_html=True)

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index[-180:], y=df['Price_Gram'].tail(180), name="History", line=dict(color="#666")))
    fig.add_trace(go.Scatter(x=future_dates, y=predictions, name="2026 Forecast", line=dict(color="#d4af37", width=4)))
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Sync Failed: {e}")
