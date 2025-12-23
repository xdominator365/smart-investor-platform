from fastapi import FastAPI, HTTPException
from services.market_data_service import MarketDataService
from services.indicator_service import IndicatorService
from services.signal_service import SignalService
from services.paper_trade_service import PaperTradeService
from fastapi.middleware.cors import CORSMiddleware

from deps import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from models.position import Position

from utils.market_hours import is_market_open
from models.auto_trade_decision import AutoTradeDecision


app = FastAPI(title="AI Investment Assistant MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/market/status")
def market_status():
    return {
        "market_open": is_market_open(),
        "timezone": "Asia/Kolkata"
    }

@app.get("/")
def home():
    return {
        "app": "MY DHIRA - Data-driven Holistic Intelligent Risk-Aware Algorithms",
        "status": "running"
    }

@app.get("/stock/{symbol}")
def stock(symbol: str):
    if not symbol or len(symbol) < 2:
        raise HTTPException(status_code=400, detail="Invalid stock symbol")

    return MarketDataService.get_latest_stock_data(symbol)


@app.get("/signal/{symbol}")
def signal(symbol: str):
    if not symbol or len(symbol) < 2:
        raise HTTPException(status_code=400, detail="Invalid stock symbol")

    df = MarketDataService.get_historical_data(symbol)
    df = IndicatorService.add_moving_averages(df)
    df = IndicatorService.add_rsi(df)

    signal_data = SignalService.generate_signal(df)
    latest = df.iloc[-1]

    return {
        "symbol": symbol.upper(),
        "current_price": round(latest["Close"], 2),
        "ma_20": round(latest["MA20"], 2),
        "ma_50": round(latest["MA50"], 2),
        "rsi": round(latest["RSI"], 2),
        **signal_data
    }

@app.post("/paper-trade/buy")
def paper_buy(symbol: str, quantity: int, db: Session = Depends(get_db)):
    stock = MarketDataService.get_latest_stock_data(symbol)
    PaperTradeService.buy(
        db,
        portfolio_id=1,
        symbol=symbol.upper(),
        price=stock["current_price"],
        quantity=quantity
    )
    return {"message": "BUY executed"}


@app.post("/paper-trade/sell")
def paper_sell(symbol: str, quantity: int, db: Session = Depends(get_db)):
    stock = MarketDataService.get_latest_stock_data(symbol)
    PaperTradeService.sell(
        db,
        portfolio_id=1,
        symbol=symbol.upper(),
        price=stock["current_price"],
        quantity=quantity
    )
    return {"message": "SELL executed"}

@app.post("/paper-trade/auto/{symbol}")
def auto_trade(symbol: str, quantity: int = 1, db: Session = Depends(get_db)):
    
    # Check market hours
    if not is_market_open():
        return {
            "signal": "N/A",
            "action": "MARKET CLOSED – AUTO TRADE SKIPPED"
        }
    
    symbol = symbol.upper()
    
    # 1️⃣ Get signal
    df = MarketDataService.get_historical_data(symbol)
    df = IndicatorService.add_moving_averages(df)
    df = IndicatorService.add_rsi(df)

    signal_data = SignalService.generate_signal(df)
    signal = signal_data["signal"]

    # 2️⃣ Get latest price
    stock = MarketDataService.get_latest_stock_data(symbol)
    price = stock["current_price"]

    # 3️⃣ Get current position from DB
    position = (
        db.query(Position)
        .filter_by(portfolio_id=1, symbol=symbol)
        .first()
    )

    current_qty = position.quantity if position else 0
    latest_rsi = df.iloc[-1]["RSI"]

    MAX_QTY_PER_SYMBOL = 10
    action = "NO ACTION"

    # 4️⃣ AUTO BUY LOGIC
    if signal == "BUY":
        if current_qty + quantity > MAX_QTY_PER_SYMBOL:
            action = "BUY BLOCKED (Max quantity reached)"
        elif latest_rsi >= 65:
            action = "BUY BLOCKED (RSI too high)"
        else:
            PaperTradeService.buy(
                db=db,
                portfolio_id=1,
                symbol=symbol,
                price=price,
                quantity=quantity,
                strategy="auto"
            )
            action = "AUTO BUY EXECUTED"

    # 5️⃣ AUTO SELL LOGIC
    elif signal == "SELL" and current_qty > 0:
        PaperTradeService.sell(
            db=db,
            portfolio_id=1,
            symbol=symbol,
            price=price,
            quantity=current_qty,
            strategy="auto"
        )
        action = "AUTO SELL EXECUTED"
    
    print(f"[AUTO-TRADE] {symbol} | Signal={signal} | RSI={latest_rsi:.2f} | Action={action}")
    
    decision = AutoTradeDecision(
    symbol=symbol,
    signal=signal,
    rsi=float(latest_rsi),
    ma20=float(df.iloc[-1]["MA20"]),
    ma50=float(df.iloc[-1]["MA50"]),
    action=action,
    reason=action  # you can refine reason text
    )

    db.add(decision)
    db.commit()

    return {
        "signal": signal,
        "action": action,
        "price": price,
        "portfolio": PaperTradeService.get_portfolio(
            db=db,
            portfolio_id=1
        )
    }
    
# To fetch decision history for a symbol
@app.get("/auto-trade/decisions/{symbol}")
def get_auto_trade_decisions(symbol: str, db: Session = Depends(get_db)):
    decisions = (
        db.query(AutoTradeDecision)
        .filter_by(symbol=symbol.upper())
        .order_by(AutoTradeDecision.created_at.desc())
        .limit(20)
        .all()
    )

    return [
        {
            "time": d.created_at,
            "signal": d.signal,
            "rsi": d.rsi,
            "ma20": d.ma20,
            "ma50": d.ma50,
            "action": d.action,
            "reason": d.reason
        }
        for d in decisions
    ]

@app.get("/chart/{symbol}")
def chart_data(symbol: str):
    df = MarketDataService.get_historical_data(symbol, period="3mo")
    df = IndicatorService.add_moving_averages(df)
    df = IndicatorService.add_rsi(df)

    df = df.dropna()

    return [
        {
            "date": str(index.date()),
            "price": round(row["Close"], 2),
            "ma20": round(row["MA20"], 2),
            "ma50": round(row["MA50"], 2),
            "rsi": round(row["RSI"], 2)
        }
        for index, row in df.iterrows()
    ]

@app.get("/paper-trade/portfolio")
def portfolio(db: Session = Depends(get_db)):
    return PaperTradeService.get_portfolio(db, portfolio_id=1)
