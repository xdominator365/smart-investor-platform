import pytest
from rules.risk_management import calculate_position_size, evaluate_exit_conditions

def test_calculate_position_size():
    # Portfolio has 100,000 cash. Max allocation is 10% (10,000). Price is 1500.
    # 10,000 / 1500 = 6.66 -> 6 shares
    shares = calculate_position_size(cash_balance=100000.0, current_price=1500.0, max_allocation_pct=0.10)
    assert shares == 6
    
    # Not enough cash to buy even 1 share with 10% rule
    shares = calculate_position_size(cash_balance=1000.0, current_price=1500.0, max_allocation_pct=0.10)
    assert shares == 0

    # 100% allocation
    shares = calculate_position_size(cash_balance=10000.0, current_price=100.0, max_allocation_pct=1.0)
    assert shares == 100

def test_evaluate_exit_conditions_safe():
    should_exit, reason = evaluate_exit_conditions(
        entry_price=100.0,
        current_price=102.0,
        peak_price=105.0,
        hard_stop_pct=-5.0,
        trailing_stop_pct=-3.0
    )
    assert should_exit is False
    assert reason == "Risk parameters OK"

def test_evaluate_exit_conditions_hard_stop():
    # Price dropped by 6% from entry
    should_exit, reason = evaluate_exit_conditions(
        entry_price=100.0,
        current_price=94.0,
        hard_stop_pct=-5.0
    )
    assert should_exit is True
    assert "Hard Stop-Loss hit" in reason

def test_evaluate_exit_conditions_trailing_stop():
    # Entry was 100, it went up to 150, but dropped back to 140 (which is >5% drop from peak, despite being +40% from entry)
    should_exit, reason = evaluate_exit_conditions(
        entry_price=100.0,
        current_price=140.0,
        peak_price=150.0,
        trailing_stop_pct=-5.0  # Sell if drops 5% from peak
    )
    assert should_exit is True
    assert "Trailing Stop-Loss hit" in reason

