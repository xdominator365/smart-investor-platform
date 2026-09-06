import sys
import os
import time

# Add project root to PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import yfinance as yf
from services.indicator_service import IndicatorService
from rules.rule_engine import run_rule_engine
from services.signal_service import SignalService
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
MAX_ALLOCATION_PCT = 0.10
HARD_STOP_PCT = -5.0

def run_backtest(symbols, period="2y"):
    print(f"--- STARTING BACKTEST OVER {period} ---")
    print(f"Universe: {len(symbols)} symbols")
    print(f"Initial Capital: Rs. {INITIAL_CAPITAL}")
    print(f"Max Allocation Per Trade: {MAX_ALLOCATION_PCT*100}%\n")
    
    total_trades = 0
    winning_trades = 0
    losing_trades = 0
    
    portfolio_cash = INITIAL_CAPITAL
    portfolio_value_history = []
    
    # Track positions: { symbol: {"qty": int, "avg_price": float, "peak": float} }
    positions = {}
    
    for symbol in symbols:
        print(f"Fetching data for {symbol}...")
        try:
            df = yf.download(symbol, period=period, interval="1d", progress=False)
            if df.empty:
                continue
            
            # If yf returns MultiIndex columns (which it often does for single ticker now), flatten it
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            # Compute indicators
            df = IndicatorService.add_moving_averages(df)
            df = IndicatorService.add_rsi(df)
            df = IndicatorService.add_atr(df)
            df = IndicatorService.add_volume_ratio(df)
            
            df = df.dropna()
            
            # Simulate daily walkthrough
            for date, row in df.iterrows():
                current_price = row["Close"]
                
                # Check Stop-Losses first
                if symbol in positions:
                    pos = positions[symbol]
                    # Update peak price
                    pos["peak"] = max(pos["peak"], current_price)
                    
                    should_exit, reason = evaluate_exit_conditions(
                        entry_price=pos["avg_price"],
                        current_price=current_price,
                        peak_price=pos["peak"],
                        hard_stop_pct=HARD_STOP_PCT
                    )
                    
                    if should_exit:
                        # Execute Sell
                        revenue = current_price * pos["qty"]
                        portfolio_cash += revenue
                        pnl = (current_price - pos["avg_price"]) * pos["qty"]
                        total_trades += 1
                        if pnl > 0: winning_trades += 1
                        else: losing_trades += 1
                        
                        del positions[symbol]
                        continue
                
                # Prepare features for Rule Engine
                features = {
                    "price": current_price,
                    "ma20": row["MA20"],
                    "ma50": row["MA50"],
                    "rsi_14": row["RSI"],
                    "rsi_slope": row["RSI_SLOPE"],
                    "volume_ratio": row["VOLUME_RATIO"],
                    "atr_percent": row["ATR_PERCENT"]
                }
                
                # We need to construct a single row df for the SignalService
                signal_df = pd.DataFrame([{
                    "Close": current_price,
                    "MA20": row["MA20"],
                    "MA50": row["MA50"],
                    "RSI": row["RSI"]
                }])
                
                rules = run_rule_engine(features)
                signal_data = SignalService.generate_signal(signal_df)
                signal = signal_data["signal"]
                
                # Evaluate Actions
                if rules["rules_passed"] and signal == "BUY" and symbol not in positions:
                    qty = calculate_position_size(portfolio_cash, current_price, MAX_ALLOCATION_PCT)
                    cost = qty * current_price
                    if qty > 0 and portfolio_cash >= cost:
                        portfolio_cash -= cost
                        positions[symbol] = {
                            "qty": qty,
                            "avg_price": current_price,
                            "peak": current_price
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
        
        # Polite delay to avoid Yahoo Finance API bans
        time.sleep(1)
            
    # Liquidate remaining positions at last close
    for sym, pos in positions.items():
        portfolio_cash += pos["qty"] * pos["avg_price"] # Assuming flat exit if still holding
        
    total_return = ((portfolio_cash - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    print("\n--- BACKTEST RESULTS ---")
    print(f"Final Portfolio Cash: Rs. {portfolio_cash:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Total Trades Executed: {total_trades}")
    print(f"Win Rate: {win_rate:.2f}%")
    
if __name__ == "__main__":
    # Test on top 50
    run_backtest(NIFTY_50, period="2y")

