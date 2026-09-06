def calculate_position_size(cash_balance: float, current_price: float, max_allocation_pct: float = 0.10) -> int:
    """
    Calculates the number of shares to buy without exceeding the maximum portfolio allocation.
    
    :param cash_balance: Total cash available in the portfolio
    :param current_price: Current market price of the asset
    :param max_allocation_pct: Maximum percentage of the portfolio to risk on a single trade (default 10%)
    :return: Integer number of shares to buy
    """
    if cash_balance <= 0 or current_price <= 0:
        return 0
        
    max_capital_to_risk = cash_balance * max_allocation_pct
    shares = int(max_capital_to_risk // current_price)
    
    return shares

def evaluate_exit_conditions(entry_price: float, current_price: float, peak_price: float | None = None, hard_stop_pct: float = -5.0, trailing_stop_pct: float = -3.0) -> tuple[bool, str]:
    """
    Evaluates if a position should be liquidated based on risk parameters.
    
    :param entry_price: The average price at which the asset was purchased
    :param current_price: The current market price
    :param peak_price: The highest price reached since purchase (for trailing stops). If None, trailing stop is ignored.
    :param hard_stop_pct: The hard stop-loss percentage (e.g. -5.0 means sell if it drops 5% below entry)
    :param trailing_stop_pct: The trailing stop-loss percentage (e.g. -3.0 means sell if it drops 3% below peak)
    :return: A tuple of (should_exit: bool, reason: str)
    """
    if entry_price <= 0 or current_price <= 0:
        return False, ""
        
    # Check hard stop loss
    return_from_entry = ((current_price - entry_price) / entry_price) * 100
    if return_from_entry <= hard_stop_pct:
        return True, f"Hard Stop-Loss hit: {return_from_entry:.2f}% (Threshold: {hard_stop_pct}%)"
        
    # Check trailing stop loss
    if peak_price and peak_price > 0:
        drawdown_from_peak = ((current_price - peak_price) / peak_price) * 100
        if drawdown_from_peak <= trailing_stop_pct:
            return True, f"Trailing Stop-Loss hit: {drawdown_from_peak:.2f}% from peak (Threshold: {trailing_stop_pct}%)"
            
    return False, "Risk parameters OK"

