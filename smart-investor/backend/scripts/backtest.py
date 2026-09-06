import sys
import os
import time

# Add project root to PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import yfinance as yf
from services.indicator_service import IndicatorService
from strategies.registry import StrategyRegistry
from rules.risk_management import calculate_position_size, evaluate_exit_conditions

# NIFTY 50 Symbols via Yahoo Finance
NIFTY_50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS",
    "SBIN.NS", "INFY.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS",
    "LT.NS", "BAJFINANCE.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TATAMOTORS.NS", "TATASTEEL.NS", "KOTAKBANK.NS", "NTPC.NS", "AXISBANK.NS",
    "TITAN.NS", "POWERGRID.NS", "ASIANPAINT.NS", "BAJAJFINSV.NS", "WIPRO.NS",
    "ONGC.NS", "ULTRACEMCO.NS", "JSWSTEEL.NS", "TECHM.NS", "ADANIENT.NS",
    "ADANIPORTS.NS", "GRASIM.NS", "HINDALCO.NS", "COALINDIA.NS", "DRREDDY.NS",
    "M&M.NS", "CIPLA.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "DIVISLAB.NS",
    "TATACONSUM.NS", "APOLLOHOSP.NS", "BRITANNIA.NS", "HEROMOTOCO.NS",
    "INDUSINDBK.NS", "LTIM.NS", "NESTLEIND.NS", "UPL.NS", "SBILIFE.NS",
    "HDFCLIFE.NS"
]

INITIAL_CAPITAL = 100000.0

def run_backtest(symbols, strategy_id="trend_follower", period="2y"):
    strategy = StrategyRegistry.get_strategy(strategy_id)
    metadata = strategy.get_metadata()
    risk_params = strategy.get_risk_parameters()
    
    print(f"--- STARTING BACKTEST OVER {period} ---")
    print(f"Strategy: {metadata['name']}")
    print(f"Expected Win Rate: {metadata['expected_win_rate']}")
    print(f"Universe: {len(symbols)} symbols")
    print(f"Initial Capital: Rs. {INITIAL_CAPITAL}")
    print(f"Max Allocation Per Trade: {risk_params['max_allocation_pct']*100}%\n")
    
    total_trades = 0
    winning_trades = 0
    losing_trades = 0
    
    portfolio_cash = INITIAL_CAPITAL
    
    # Track positions: { symbol: {"qty": int, "avg_price": float, "peak": float, "days_held": int} }
    positions = {}
    
    for symbol in symbols:
        try:
            df = yf.download(symbol, period=period, interval="1d", progress=False)
            if df.empty:
                continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            df = IndicatorService.add_moving_averages(df)
            # Add MA200 explicitly for mean reversion
            df["MA200"] = df["Close"].rolling(window=200).mean() 
            df = IndicatorService.add_rsi(df)
            df = IndicatorService.add_atr(df)
            df = IndicatorService.add_volume_ratio(df)
            
            # Simulate daily walkthrough
            for date, row in df.iterrows():
                current_price = row["Close"]
                
                # Check Stop-Losses & Time Exits first
                if symbol in positions:
                    pos = positions[symbol]
                    pos["peak"] = max(pos["peak"], current_price)
                    pos["days_held"] += 1
                    
                    should_exit, reason = evaluate_exit_conditions(
                        entry_price=pos["avg_price"],
                        current_price=current_price,
                        peak_price=pos["peak"],
                        hard_stop_pct=risk_params["hard_stop_pct"],
                        trailing_stop_pct=risk_params.get("trailing_stop_pct", -10.0)
                    )
                    
                    # Check max hold days constraint
                    if pos["days_held"] >= risk_params.get("max_hold_days", 365):
                        should_exit = True
                        reason = "Time Exit: Max hold days reached."
                    
                    if should_exit:
                        revenue = current_price * pos["qty"]
                        portfolio_cash += revenue
                        pnl = (current_price - pos["avg_price"]) * pos["qty"]
                        total_trades += 1
                        if pnl > 0: winning_trades += 1
                        else: losing_trades += 1
                        
                        del positions[symbol]
                        continue
                
                # We need to construct a df up to the current date for the strategy
                # For speed in this simple backtest, we just pass the single row wrapped in a DF
                signal_df = pd.DataFrame([{
                    "Close": current_price,
                    "MA20": row["MA20"],
                    "MA50": row["MA50"],
                    "MA200": row["MA200"],
                    "RSI": row["RSI"]
                }])
                
                signal_data = strategy.generate_signal(signal_df)
                signal = signal_data["signal"]
                
                # Evaluate Actions
                if signal == "BUY" and symbol not in positions:
                    qty = calculate_position_size(portfolio_cash, current_price, risk_params["max_allocation_pct"])
                    cost = qty * current_price
                    if qty > 0 and portfolio_cash >= cost:
                        portfolio_cash -= cost
                        positions[symbol] = {
                            "qty": qty,
                            "avg_price": current_price,
                            "peak": current_price,
                            "days_held": 0
                        }
                elif signal == "SELL" and symbol in positions:
                    pos = positions[symbol]
                    revenue = current_price * pos["qty"]
                    portfolio_cash += revenue
                    pnl = (current_price - pos["avg_price"]) * pos["qty"]
                    
                    total_trades += 1
                    if pnl > 0: winning_trades += 1
                    else: losing_trades += 1
                    del positions[symbol]
                    
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            
    # Liquidate remaining positions at last close
    for sym, pos in positions.items():
        portfolio_cash += pos["qty"] * pos["avg_price"]
        
    total_return = ((portfolio_cash - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    print("\n--- BACKTEST RESULTS ---")
    print(f"Final Portfolio Cash: Rs. {portfolio_cash:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Total Trades Executed: {total_trades}")
    print(f"Win Rate: {win_rate:.2f}%\n")
    
if __name__ == "__main__":
    print("Testing Strategy 1: Trend Following")
    run_backtest(NIFTY_50, strategy_id="trend_follower", period="3y")
    print("-" * 50)
    print("Testing Strategy 2: Mean Reversion")
    run_backtest(NIFTY_50, strategy_id="mean_reversion", period="3y")

