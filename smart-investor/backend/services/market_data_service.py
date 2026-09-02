import yfinance as yf
import pandas as pd
from fastapi import HTTPException


class MarketDataService:

    @staticmethod
    def get_latest_stock_data(symbol: str, interval: str = "1m") -> dict:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d", interval=interval, auto_adjust=True)

        if data.empty:
            raise HTTPException(
                status_code=404,
                detail="No market data available for this symbol"
            )

        latest = data.iloc[-1]

        def safe(value, default=0.0):
            return default if pd.isna(value) else value

        close_price = safe(latest.get("Close"))

        if close_price <= 0:
            raise HTTPException(
                status_code=422,
                detail="Invalid price data received"
            )

        return {
            "symbol": symbol.upper(),
            "current_price": round(close_price, 2),
            "open": round(safe(latest.get("Open")), 2),
            "high": round(safe(latest.get("High")), 2),
            "low": round(safe(latest.get("Low")), 2),
            "volume": int(safe(latest.get("Volume"), 0))
        }

    @staticmethod
    def get_historical_data(symbol: str, period="3mo") -> pd.DataFrame:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, auto_adjust=True)

        if data.empty:
            raise HTTPException(
                status_code=404,
                detail="No historical data available"
            )

        return data
