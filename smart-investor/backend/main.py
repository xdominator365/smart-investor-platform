from fastapi import FastAPI, HTTPException
from services.market_data_service import MarketDataService
from services.indicator_service import IndicatorService
from services.signal_service import SignalService
from services.paper_trade_service import PaperTradeService
from services.decision_context_service import DecisionContextService
from fastapi.middleware.cors import CORSMiddleware

from deps import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from models.position import Position

from utils.market_hours import is_market_open
from models.auto_trade_decision import AutoTradeDecision

from services.news_service import NewsService


app = FastAPI(title="AI Investment Assistant MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://dhira-fv9909tn3-xdominator365s-projects.vercel.app"
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
def signal(symbol: str, db: Session = Depends(get_db)):
    if not symbol or len(symbol) < 2:
        raise HTTPException(status_code=400, detail="Invalid stock symbol")

    df = MarketDataService.get_historical_data(symbol)
    df = IndicatorService.add_moving_averages(df)
    df = IndicatorService.add_rsi(df)

    signal_data = SignalService.generate_signal(df)
    news_insights = NewsService.build_insight(db, symbol)
    latest = df.iloc[-1]

    return {
        "symbol": symbol.upper(),
        "current_price": round(latest["Close"], 2),
        "ma_20": round(latest["MA20"], 2),
        "ma_50": round(latest["MA50"], 2),
        "rsi": round(latest["RSI"], 2),
        **signal_data,
        "news_insights": news_insights
    }

@app.post("/paper-trade/buy")
def paper_buy(symbol: str, quantity: int, db: Session = Depends(get_db)):
    context = DecisionContextService.build(symbol, db=db)

    rules = context["rules"]
    warnings = None

    if not rules["rules_passed"]:
        warnings = f"Trade executed with rule warnings: {rules['blocked_by']}"


    stock = MarketDataService.get_latest_stock_data(symbol)

    PaperTradeService.buy(
        db=db,
        portfolio_id=1,
        symbol=symbol.upper(),
        price=stock["current_price"],
        quantity=quantity
    )

    return {"message": "BUY executed", "rules": rules, "warnings": warnings}


@app.post("/paper-trade/sell")
def paper_sell(symbol: str, quantity: int, db: Session = Depends(get_db)):
    context = DecisionContextService.build(symbol, db=db)

    rules = context["rules"]
    warnings = None

    if not rules["rules_passed"]:
        warnings = f"Trade executed with rule warnings: {rules['blocked_by']}"


    stock = MarketDataService.get_latest_stock_data(symbol)

    PaperTradeService.sell(
        db=db,
        portfolio_id=1,
        symbol=symbol.upper(),
        price=stock["current_price"],
        quantity=quantity
    )

    return {"message": "SELL executed", "rules": rules, "warnings": warnings}

@app.post("/paper-trade/auto/{symbol}")
def auto_trade(symbol: str, quantity: int = 1, db: Session = Depends(get_db)):

    if not is_market_open():
        return {"action": "MARKET CLOSED"}

    symbol = symbol.upper()
    
    context = DecisionContextService.build(symbol, db=db)
    features = context["features"]
    rules = context["rules"]
    df = context["df"]
    snapshot = context["snapshot"]

    signal_data = SignalService.generate_signal(df)
    signal = signal_data["signal"]

    stock = MarketDataService.get_latest_stock_data(symbol)
    price = stock["current_price"]

    position = db.query(Position).filter_by(
        portfolio_id=1, symbol=symbol
    ).first()

    current_qty = position.quantity if position else 0
    action = "NO ACTION"

    if not rules["rules_passed"]:
        action = f"BLOCKED BY RULES: {rules['blocked_by']}"

    elif signal == "BUY":
        PaperTradeService.buy(
            db=db,
            portfolio_id=1,
            symbol=symbol,
            price=price,
            quantity=quantity,
            strategy="auto"
        )
        action = "AUTO BUY EXECUTED"

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

    decision = AutoTradeDecision(
        symbol=symbol,
        signal=signal,
        rsi=features["rsi_14"],
        ma20=features["ma20"],
        ma50=features["ma50"],
        action=action,
        reason=action
    )

    db.add(decision)
    db.commit()

    return {
        "signal": signal,
        "action": action,
        "rules": rules
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

# NEWS INGESTION AND SENTIMENT ANALYSIS ENDPOINTS

@app.post("/news/ingest/{symbol}")
def ingest_news(symbol: str, db: Session = Depends(get_db)):
    return NewsService.ingest_news(db, symbol)

@app.get("/news/insights/{symbol}")
def news_insights(symbol: str, db: Session = Depends(get_db)):
    return NewsService.build_insight(db, symbol)
