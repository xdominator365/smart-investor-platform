import pandas as pd


class SignalService:

    @staticmethod
    def generate_signal(df: pd.DataFrame, news_insights: dict | None = None) -> dict:
        
        required_cols = {"MA20", "MA50", "RSI"}
        missing = required_cols - set(df.columns)

        if missing:
            raise ValueError(f"Missing indicators: {missing}")

        latest = df.iloc[-1]

        if pd.isna(latest["MA20"]) or pd.isna(latest["MA50"]) or pd.isna(latest["RSI"]):
            return {
                "signal": "HOLD",
                "confidence": 0,
                "reason": "Indicators not fully formed"
            }

        price = latest["Close"]
        ma_gap = abs(latest["MA20"] - latest["MA50"])

        confidence = round(min((ma_gap / price) * 100, 100), 2) if price > 0 else 0

        if ma_gap < 0.001 * price:
            signal = "HOLD"
            reason = "No clear trend (MAs too close)"
        elif latest["MA20"] > latest["MA50"] and latest["RSI"] < 70:
            signal = "BUY"
            reason = "Uptrend confirmed and RSI not overbought"
        elif latest["MA20"] < latest["MA50"] and latest["RSI"] > 30:
            signal = "SELL"
            reason = "Downtrend confirmed and RSI not oversold"
        else:
            signal = "HOLD"
            reason = "Trend and momentum do not align"

        news_bias = None
        sentiment = (news_insights or {}).get("sentiment")
        if sentiment:
            news_bias = round(
                0.6 * float(sentiment.get("avg_24h", 0))
                + 0.4 * float(sentiment.get("avg_7d", 0)),
                3,
            )

            if signal == "BUY" and news_bias < -0.2:
                signal = "HOLD"
                reason = "Uptrend confirmed, but negative news sentiment increases risk"
            elif signal == "SELL" and news_bias > 0.2:
                signal = "HOLD"
                reason = "Downtrend confirmed, but positive news sentiment reduces conviction"
            elif signal == "BUY":
                reason = f"{reason}; news sentiment supports the setup"
            elif signal == "SELL":
                reason = f"{reason}; news sentiment supports the setup"
            else:
                reason = f"{reason}; news sentiment is {sentiment.get('label', 'NEUTRAL').lower()}"

        return {
            "signal": signal,
            "confidence": confidence,
            "reason": reason,
            "news_bias": news_bias,
        }