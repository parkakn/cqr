import yfinance as yf
import pandas as pd
import numpy as np

class technicalindicator:
    def get_moving_average(df, period):
        ma = df.rolling(period).mean().dropna()
        ma.columns = [f'{col}_ma5' for col in ma.columns]
        return ma

    def calculate_macd(price_series):
        ema_12 = price_series.ewm(span=12, adjust=False).mean()
        ema_26 = price_series.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal_line = macd.ewm(span=9, adjust=False).mean()
        return macd, signal_line