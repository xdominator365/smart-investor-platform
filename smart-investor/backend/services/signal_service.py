import pandas as pd


class SignalService:

    @staticmethod
    def generate_signal(df: pd.DataFrame) -> dict:
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

        return {
            "signal": signal,
            "confidence": confidence,
            "reason": reason
        }