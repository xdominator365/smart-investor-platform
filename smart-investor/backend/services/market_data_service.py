import yfinance as yf
import pandas as pd
from fastapi import HTTPException


class MarketDataService:

    @staticmethod
    def _safe_numeric(value, default=0.0):
        return default if pd.isna(value) else float(value)

    @staticmethod
    def _calculate_return_percent(data: pd.DataFrame, lookback_days: int) -> float:
        if data.empty or len(data) <= lookback_days:
            return 0.0

        current_close = MarketDataService._safe_numeric(data.iloc[-1].get("Close"))
        previous_close = MarketDataService._safe_numeric(
            data.iloc[-(lookback_days + 1)].get("Close")
        )

        if previous_close <= 0:
            return 0.0

        return round(((current_close - previous_close) / previous_close) * 100, 2)

    @staticmethod
    def get_latest_stock_data(symbol: str) -> dict:
        stock = yf.Ticker(symbol)
        data = stock.history(period="3mo", auto_adjust=True)

        if data.empty:
            raise HTTPException(
                status_code=404,
                detail="No market data available for this symbol"
            )

        latest = data.iloc[-1]

        close_price = MarketDataService._safe_numeric(latest.get("Close"))

        if close_price <= 0:
            raise HTTPException(
                status_code=422,
                detail="Invalid price data received"
            )

        return {
            "symbol": symbol.upper(),
            "current_price": round(close_price, 2),
            "open": round(MarketDataService._safe_numeric(latest.get("Open")), 2),
            "high": round(MarketDataService._safe_numeric(latest.get("High")), 2),
            "low": round(MarketDataService._safe_numeric(latest.get("Low")), 2),
            "volume": int(MarketDataService._safe_numeric(latest.get("Volume"), 0)),
            "return_1d": MarketDataService._calculate_return_percent(data, 1),
            "return_5d": MarketDataService._calculate_return_percent(data, 5),
            "return_30d": MarketDataService._calculate_return_percent(data, 30),
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
