import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def get_market_data(tax_factor=1.092):
    # Fetch 2 years of history
    gold = yf.download("GC=F", period="2y", interval="1d", progress=False)
    inr = yf.download("INR=X", period="2y", interval="1d", progress=False)
    
    if isinstance(gold.columns, pd.MultiIndex): gold.columns = gold.columns.get_level_values(0)
    if isinstance(inr.columns, pd.MultiIndex): inr.columns = inr.columns.get_level_values(0)

    df = pd.merge(gold[['Close']], inr[['Close']].rename(columns={'Close':'USDINR'}), 
                 left_index=True, right_index=True).dropna()
    
    df['Price_Gram'] = (df['Close'] / 31.1034768) * df['USDINR'] * tax_factor
    return df

def run_forecast(df):
    df_m = df.reset_index()
    df_m['Ordinal'] = df_m['Date'].map(pd.Timestamp.toordinal)
    
    # Train on Bullish Momentum (last 120 days)
    model = LinearRegression().fit(df_m.tail(120)[['Ordinal']], df_m.tail(120)['Price_Gram'])
    
    future_months = pd.date_range(start="2026-01-01", end="2026-12-01", freq='MS')
    future_ord = np.array([d.toordinal() for d in future_months]).reshape(-1, 1)
    preds = model.predict(future_ord)
    
    return future_months, preds
