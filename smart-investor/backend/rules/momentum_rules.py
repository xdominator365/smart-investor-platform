def evaluate_rsi(rsi, rsi_slope):
    if rsi < 70 and rsi_slope > 0:
        return True, f"RSI healthy ({rsi:.2f}) and rising"
    if rsi >= 70:
        return False, f"RSI overbought ({rsi:.2f})"
    return False, f"RSI weak ({rsi:.2f})"
