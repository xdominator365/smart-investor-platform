from services.market_data_service import MarketDataService
from services.indicator_service import IndicatorService
from rules.rule_engine import run_rule_engine
from models.ml_feature_snapshot import MLFeatureSnapshot



class DecisionContextService:

    @staticmethod
    def build(symbol: str, db=None):
        # 1Fetch historical data
        df = MarketDataService.get_historical_data(symbol)

        # Compute indicators
        df = IndicatorService.add_moving_averages(df)
        df = IndicatorService.add_rsi(df)
        df = IndicatorService.add_atr(df)
        df = IndicatorService.add_volume_ratio(df)

        df = df.dropna()
        latest = df.iloc[-1]

        # Build feature dictionary
        features = {
            "price": float(latest["Close"]),
            "ma20": float(latest["MA20"]),
            "ma50": float(latest["MA50"]),
            "rsi_14": float(latest["RSI"]),
            "rsi_slope": float(latest["RSI_SLOPE"]),
            "volume_ratio": float(latest["VOLUME_RATIO"]),
            "atr_percent": float(latest["ATR_PERCENT"]),
        }

        # Run rule engine
        rule_output = run_rule_engine(features)
        
        # PERSIST SNAPSHOT (ONLY IF DB IS PROVIDED)
        snapshot = None
        if db:
            snapshot = MLFeatureSnapshot(
                symbol=symbol.upper(),
                price=features["price"],
                ma20=features["ma20"],
                ma50=features["ma50"],
                rsi_14=features["rsi_14"],
                rsi_slope=features["rsi_slope"],
                volume_ratio=features["volume_ratio"],
                atr_percent=features["atr_percent"],
                rule_trend_ok=rule_output["rule_trend_ok"],
                rule_rsi_ok=rule_output["rule_rsi_ok"],
                rule_volume_ok=rule_output["rule_volume_ok"],
                rule_volatility_ok=rule_output["rule_volatility_ok"],
                rules_passed=rule_output["rules_passed"],
                risk_level=rule_output["risk_level"],
            )

            db.add(snapshot)
            db.commit()
            db.refresh(snapshot)

        return {
            "features": features,
            "rules": rule_output,
            "df": df,
            "snapshot": snapshot
        }
        