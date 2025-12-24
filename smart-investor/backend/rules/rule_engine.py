# BRAIN OF RULES - RULES ENGINE ORCHESTRATOR
from rules.trend_rules import evaluate_trend
from rules.momentum_rules import evaluate_rsi
from rules.volume_rules import evaluate_volume
from rules.volatility_rules import evaluate_volatility


def run_rule_engine(features: dict):
    explanations = {}
    blocked_by = []

    trend_ok, trend_reason = evaluate_trend(
        features["price"],
        features["ma20"],
        features["ma50"],
    )
    explanations["trend"] = trend_reason
    if not trend_ok:
        blocked_by.append("TREND")

    rsi_ok, rsi_reason = evaluate_rsi(
        features["rsi_14"],
        features["rsi_slope"],
    )
    explanations["rsi"] = rsi_reason
    if not rsi_ok:
        blocked_by.append("RSI")

    volume_ok, volume_reason = evaluate_volume(
        features["volume_ratio"]
    )
    explanations["volume"] = volume_reason
    if not volume_ok:
        blocked_by.append("VOLUME")

    volatility_ok, vol_reason = evaluate_volatility(
        features["atr_percent"]
    )
    explanations["volatility"] = vol_reason
    if not volatility_ok:
        blocked_by.append("VOLATILITY")

    rules_passed = all([trend_ok, rsi_ok, volume_ok, volatility_ok])

    if not volatility_ok:
        risk_level = "HIGH"
    elif not rsi_ok:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "rules_passed": rules_passed,
        "risk_level": risk_level,
        "blocked_by": blocked_by,
        "explanations": explanations,
        "rule_trend_ok": trend_ok,
        "rule_rsi_ok": rsi_ok,
        "rule_volume_ok": volume_ok,
        "rule_volatility_ok": volatility_ok,
    }
