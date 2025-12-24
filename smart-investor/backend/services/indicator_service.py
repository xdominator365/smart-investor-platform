import pandas as pd
import numpy as np


class IndicatorService:

    @staticmethod
    def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["MA50"] = df["Close"].rolling(window=50).mean()
        return df

    @staticmethod
    def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        delta = df["Close"].diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["RSI"] = 100 - (100 / (1 + rs))
        df["RSI_SLOPE"] = df["RSI"].diff()

        return df
    
    @staticmethod
    def add_atr(df, period=14):
        high_low = df["High"] - df["Low"]
        high_close = (df["High"] - df["Close"].shift()).abs()
        low_close = (df["Low"] - df["Close"].shift()).abs()

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)

        df["ATR"] = true_range.rolling(period).mean()
        df["ATR_PERCENT"] = (df["ATR"] / df["Close"]) * 100

        return df

    @staticmethod
    def add_volume_ratio(df, period=20):
        df["AVG_VOLUME"] = df["Volume"].rolling(period).mean()
        df["VOLUME_RATIO"] = df["Volume"] / df["AVG_VOLUME"]
        return df
    