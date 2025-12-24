def evaluate_trend(price, ma20, ma50):
    if price > ma20 and ma20 > ma50:
        return True, "Price above MA20 and MA50 (uptrend)"
    return False, "Trend not aligned (price below key MAs)"