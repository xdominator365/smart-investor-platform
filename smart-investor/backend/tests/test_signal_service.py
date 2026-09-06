import pytest
import pandas as pd
from services.signal_service import SignalService

def create_mock_dataframe(close, ma20, ma50, rsi):
    """Helper to create a single-row dataframe that SignalService expects"""
    return pd.DataFrame([{
        "Close": close,
        "MA20": ma20,
        "MA50": ma50,
        "RSI": rsi
    }])

def test_signal_buy():
    # Strong uptrend, not overbought
    df = create_mock_dataframe(close=110, ma20=105, ma50=100, rsi=55)
    result = SignalService.generate_signal(df)
    
    assert result["signal"] == "BUY"
    assert "Uptrend" in result["reason"]
    assert result["confidence"] > 0

def test_signal_sell():
    # Strong downtrend, not oversold
    df = create_mock_dataframe(close=90, ma20=95, ma50=100, rsi=45)
    result = SignalService.generate_signal(df)
    
    assert result["signal"] == "SELL"
    assert "Downtrend" in result["reason"]

def test_signal_hold_no_clear_trend():
    # MA20 and MA50 are too close (within 0.1% buffer)
    df = create_mock_dataframe(close=100, ma20=100.05, ma50=100.0, rsi=50)
    result = SignalService.generate_signal(df)
    
    assert result["signal"] == "HOLD"
    assert "No clear trend" in result["reason"]

def test_signal_news_overlay_downgrade():
    # Technicals say BUY, but news is extremely negative
    df = create_mock_dataframe(close=110, ma20=105, ma50=100, rsi=55)
    bad_news = {
        "sentiment": {
            "avg_24h": -0.8,
            "avg_7d": -0.8
        }
    }
    
    result = SignalService.generate_signal(df, news_insights=bad_news)
    
    # News should downgrade the BUY signal to HOLD
    assert result["signal"] == "HOLD"
    assert "negative news sentiment increases risk" in result["reason"]

def test_signal_news_overlay_upgrade():
    # Technicals say BUY, and news supports it
    df = create_mock_dataframe(close=110, ma20=105, ma50=100, rsi=55)
    good_news = {
        "sentiment": {
            "avg_24h": 0.9,
            "avg_7d": 0.9,
            "label": "POSITIVE"
        }
    }
    
    result = SignalService.generate_signal(df, news_insights=good_news)
    
    assert result["signal"] == "BUY"
    assert "news sentiment supports the setup" in result["reason"]

