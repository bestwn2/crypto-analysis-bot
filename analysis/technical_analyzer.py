# analysis/technical_analyzer.py
import pandas_ta as ta

def analyze_data(df):
    """
    ئیندیکەیتەرە تەکنیکییەکان بۆ DataFrame زیاد دەکات
    """
    if df is None or df.empty:
        return None
    
    # زیادکردنی ستراتیژییەکانی TA بە بەکارهێنانی pandas_ta
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    df.ta.ema(length=50, append=True)  # EMA 50
    df.ta.ema(length=200, append=True) # EMA 200
    
    # دڵنیابوونەوە لەوەی هیچ NaN value بوونی نییە
    df.dropna(inplace=True)
    return df