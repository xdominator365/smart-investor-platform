def evaluate_volatility(atr_percent):
    if atr_percent < 3:
        return True, f"Volatility acceptable ({atr_percent:.2f}%)"
    return False, f"High volatility ({atr_percent:.2f}%)"
