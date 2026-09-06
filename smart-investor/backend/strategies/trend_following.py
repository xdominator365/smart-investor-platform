import pandas as pd
from .base_strategy import TradingStrategy

class TrendFollowingStrategy(TradingStrategy):
    
    @classmethod
    def get_id(cls) -> str:
        return "trend_follower"
        
    @classmethod
    def get_metadata(cls) -> dict:
        return {
            "name": "Ride the Wave (Trend Follower)",
            "description": "Buys stocks that are already going up and rides the wave. Wins less often, but aims for huge profits when it does catch a long trend.",
            "expected_win_rate": "~35-40%",
            "risk_level": "High Risk / High Reward"
        }
        
    @classmethod
    def get_risk_parameters(cls) -> dict:
        return {
            "hard_stop_pct": -5.0,
            "trailing_stop_pct": -10.0, # Give trend room to breathe
            "max_allocation_pct": 0.10,
            "max_hold_days": 365 # Hold as long as the trend lasts
        }
        
    @classmethod
    def generate_signal(cls, df: pd.DataFrame, news_insights: dict | None = None) -> dict:
        required_cols = {"MA20", "MA50", "RSI"}
        missing = required_cols - set(df.columns)

        if missing:
            raise ValueError(f"Missing data needed for strategy: {missing}")

        latest = df.iloc[-1]

        if pd.isna(latest["MA20"]) or pd.isna(latest["MA50"]) or pd.isna(latest["RSI"]):
            return {
                "signal": "HOLD",
                "confidence": 0,
                "reason": "Not enough historical data to make a decision yet."
            }

        price = latest["Close"]
        ma_gap = abs(latest["MA20"] - latest["MA50"])
        confidence = round(min((ma_gap / price) * 100, 100), 2) if price > 0 else 0

        # Beginner friendly logic strings
        if ma_gap < 0.001 * price:
            signal = "HOLD"
            reason = "The stock is moving sideways right now. It's best to wait until a clear direction forms."
        elif latest["MA20"] > latest["MA50"] and latest["RSI"] < 70:
            signal = "BUY"
            reason = "The stock is clearly going up! It hasn't peaked yet, so it's a good time to jump on the wave."
        elif latest["MA20"] < latest["MA50"] and latest["RSI"] > 30:
            signal = "SELL"
            reason = "The stock is starting to fall. It's time to sell and protect your money."
        else:
            signal = "HOLD"
            reason = "The market is mixed right now, so it's safer to just hold and wait."

        # News overlay
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
                reason = "The price looks good to buy, but there is a lot of bad news right now. It's safer to wait."
            elif signal == "SELL" and news_bias > 0.2:
                signal = "HOLD"
                reason = "The price is dropping, but there is very positive news out. The stock might bounce back, so we will hold."
            elif signal == "BUY":
                reason = f"{reason} Also, the news is positive, giving us extra confidence!"
            elif signal == "SELL":
                reason = f"{reason} Also, the news is negative, confirming we should sell."
            else:
                pass # Keep original reason

        return {
            "signal": signal,
            "confidence": confidence,
            "reason": reason,
            "news_bias": news_bias,
        }

