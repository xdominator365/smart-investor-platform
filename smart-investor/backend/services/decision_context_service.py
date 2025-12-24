from services.market_data_service import MarketDataService
from services.indicator_service import IndicatorService
from rules.rule_engine import run_rule_engine


class DecisionContextService:

    @staticmethod
    def build(symbol: str):
        # 1️⃣ Fetch historical data
        df = MarketDataService.get_historical_data(symbol)

        # 2️⃣ Compute indicators
        df = IndicatorService.add_moving_averages(df)
        df = IndicatorService.add_rsi(df)
        df = IndicatorService.add_atr(df)
        df = IndicatorService.add_volume_ratio(df)

        df = df.dropna()
        latest = df.iloc[-1]

        # 3️⃣ Build feature dictionary
        features = {
            "price": float(latest["Close"]),
            "ma20": float(latest["MA20"]),
            "ma50": float(latest["MA50"]),
            "rsi_14": float(latest["RSI"]),
            "rsi_slope": float(latest["RSI_SLOPE"]),
            "volume_ratio": float(latest["VOLUME_RATIO"]),
            "atr_percent": float(latest["ATR_PERCENT"]),
        }

        # 4️⃣ Run rule engine
        rule_output = run_rule_engine(features)

        return {
            "features": features,
            "rules": rule_output,
            "df": df
        }
        