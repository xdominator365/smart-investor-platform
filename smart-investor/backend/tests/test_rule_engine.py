import pytest
from rules.rule_engine import run_rule_engine

def test_rule_engine_all_pass():
    # Setup perfect conditions for a trade
    features = {
        "price": 105.0,
        "ma20": 100.0,
        "ma50": 90.0,           # Trend: OK (100 > 90)
        "rsi_14": 50.0,         # Momentum: OK (30 < 50 < 70)
        "rsi_slope": 1.0,
        "volume_ratio": 2.0,    # Volume: OK (>= 1.5)
        "atr_percent": 2.0      # Volatility: OK (< 3)
    }
    
    result = run_rule_engine(features)
    
    assert result["rule_trend_ok"] is True
    assert result["rule_rsi_ok"] is True
    assert result["rule_volume_ok"] is True
    assert result["rule_volatility_ok"] is True
    assert result["rules_passed"] is True
    assert len(result["blocked_by"]) == 0

def test_rule_engine_trend_fails():
    # Setup failing trend (MA20 < MA50)
    features = {
        "price": 85.0,
        "ma20": 90.0,
        "ma50": 100.0,          # Trend: FAIL
        "rsi_14": 50.0,
        "rsi_slope": 1.0,
        "volume_ratio": 2.0,
        "atr_percent": 2.0
    }
    
    result = run_rule_engine(features)
    
    assert result["rule_trend_ok"] is False
    assert result["rules_passed"] is False
    assert "TREND" in result["blocked_by"]

def test_rule_engine_overbought():
    # Setup RSI overbought condition
    features = {
        "price": 105.0,
        "ma20": 100.0,
        "ma50": 90.0,
        "rsi_14": 75.0,         # Momentum: FAIL (> 70)
        "rsi_slope": 1.0,
        "volume_ratio": 2.0,
        "atr_percent": 2.0
    }
    
    result = run_rule_engine(features)
    
    assert result["rule_rsi_ok"] is False
    assert result["rules_passed"] is False
    assert "RSI" in result["blocked_by"]

def test_rule_engine_high_volatility():
    # Setup high volatility condition
    features = {
        "price": 105.0,
        "ma20": 100.0,
        "ma50": 90.0,
        "rsi_14": 50.0,
        "rsi_slope": 1.0,
        "volume_ratio": 2.0,
        "atr_percent": 4.0      # Volatility: FAIL (>= 3)
    }
    
    result = run_rule_engine(features)
    
    assert result["rule_volatility_ok"] is False
    assert result["rules_passed"] is False
    assert "VOLATILITY" in result["blocked_by"]

