import pandas as pd
from .base_strategy import TradingStrategy

class MeanReversionStrategy(TradingStrategy):
    
    @classmethod
    def get_id(cls) -> str:
        return "mean_reversion"
        
    @classmethod
    def get_metadata(cls) -> dict:
        return {
            "name": "Buy the Dip (Safe Pullbacks)",
            "description": "Buys strong companies when they go on a temporary sale. Wins very often by taking small, steady profits quickly.",
            "expected_win_rate": "~60-70%",
            "risk_level": "Low Risk / Steady Reward"
        }
        
    @classmethod
    def get_risk_parameters(cls) -> dict:
        return {
            "hard_stop_pct": -3.0, # Tight stop, if the dip keeps dipping, get out
            "trailing_stop_pct": -3.0, 
            "max_allocation_pct": 0.10,
            "max_hold_days": 10 # If it doesn't bounce in 10 days, the thesis is wrong
        }
        
    @classmethod
    def generate_signal(cls, df: pd.DataFrame, news_insights: dict | None = None) -> dict:
        # We need MA200 for macro trend, but we might not have it if data is too short.
        # So we'll use MA50 and RSI for short term panics.
        required_cols = {"MA50", "RSI"}
        missing = required_cols - set(df.columns)

        if missing:
            raise ValueError(f"Missing data needed for strategy: {missing}")

        latest = df.iloc[-1]

        if pd.isna(latest["MA50"]) or pd.isna(latest["RSI"]):
            return {
                "signal": "HOLD",
                "confidence": 0,
                "reason": "Not enough historical data to make a decision yet."
            }

        price = latest["Close"]
        
        # We assume df has MA200 if calculated, else fallback to MA50 trend
        macro_is_up = True
        if "MA200" in df.columns and not pd.isna(latest["MA200"]):
            macro_is_up = latest["MA50"] > latest["MA200"]
        elif "MA20" in df.columns and not pd.isna(latest["MA20"]):
             # Fallback if MA200 isn't available
             macro_is_up = latest["MA20"] > latest["MA50"]

        rsi = latest["RSI"]

        if macro_is_up and rsi < 35:
            signal = "BUY"
            reason = "This is a very strong stock that just dropped in price due to temporary panic. It is on a great discount right now!"
            confidence = 80.0
        elif rsi > 70:
            signal = "SELL"
            reason = "The stock has bounced back up and is highly priced. Let's sell now and lock in our profits."
            confidence = 90.0
        else:
            signal = "HOLD"
            reason = "The stock is behaving normally. We only buy when there is an extreme discount."
            confidence = 50.0

        # News overlay
        news_bias = None
        sentiment = (news_insights or {}).get("sentiment")
        if sentiment:
            news_bias = round(
                0.6 * float(sentiment.get("avg_24h", 0))
                + 0.4 * float(sentiment.get("avg_7d", 0)),
                3,
            )

            if signal == "BUY" and news_bias < -0.4:
                # Need REALLY bad news to cancel a mean reversion buy, because panic is expected
                signal = "HOLD"
                reason = "The stock is on discount, but the news is extremely toxic right now. It's too dangerous to buy."
            elif signal == "SELL" and news_bias > 0.4:
                # Extremely good news? Maybe hold a bit longer
                signal = "HOLD"
                reason = "We were going to take profits, but amazing news just came out! Let's hold and see if it goes higher."

        return {
            "signal": signal,
            "confidence": confidence,
            "reason": reason,
            "news_bias": news_bias,
        }

