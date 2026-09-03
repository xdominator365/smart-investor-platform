import asyncio
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from pydantic import BaseModel
from models.user import User
from models.portfolio import Portfolio

from fastapi import FastAPI, HTTPException, Header, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from services.market_data_service import MarketDataService
from services.indicator_service import IndicatorService
from services.signal_service import SignalService
from services.paper_trade_service import PaperTradeService
from services.decision_context_service import DecisionContextService
from services.market_stream_service import MarketStreamService
from fastapi.middleware.cors import CORSMiddleware

from deps import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from models.position import Position
from models.broker_order import BrokerOrder

from utils.market_hours import is_market_open
from models.auto_trade_decision import AutoTradeDecision

from services.news_service import NewsService
from services.zerodha_service import ZerodhaService


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
    allow_headers=[
        "Content-Type",
        "X-Guest-ID"
    ],
)

class SessionRequest(BaseModel):
    guest_id: str


class ZerodhaOrderPreviewRequest(BaseModel):
    symbol: str
    side: str
    quantity: int
    reference_price: float


class ZerodhaOrderRequest(BaseModel):
    preview_id: str
    idempotency_key: str
    confirmed: bool


market_stream_manager = MarketStreamService(refresh_interval=15)


@app.on_event("startup")
async def startup_event():
    app.state.market_stream_task = asyncio.create_task(market_stream_manager.run())


@app.on_event("shutdown")
async def shutdown_event():
    task = getattr(app.state, "market_stream_task", None)
    if task is not None:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    await market_stream_manager.shutdown()


@app.websocket("/ws/market")
async def market_websocket(websocket: WebSocket):
    await market_stream_manager.connect(websocket)

    try:
        while True:
            payload = await websocket.receive_json()
            await market_stream_manager.handle_message(websocket, payload)
    except WebSocketDisconnect:
        await market_stream_manager.disconnect(websocket)
    except Exception:
        await market_stream_manager.disconnect(websocket)


@app.post("/session")
def create_session(
    request: SessionRequest,
    db: Session = Depends(get_db)
):
    guest_id = request.guest_id.strip()

    if not guest_id:
        raise HTTPException(
            status_code=400,
            detail="guest_id is required"
        )

    # 1. Find existing guest user
    user = (
        db.query(User)
        .filter(User.guest_id == guest_id)
        .first()
    )

    # 2. Create user if this is a new visitor
    if not user:
        user = User(
            guest_id=guest_id,
            email=None,
            name="Guest User"
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    # 3. Find this user's portfolio
    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.user_id == user.id)
        .first()
    )

    # 4. Create fresh paper portfolio only once
    if not portfolio:
        portfolio = Portfolio(
            user_id=user.id,
            name="Paper Portfolio",
            cash_balance=100000.0
        )

        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)

    return {
        "user_id": user.id,
        "guest_id": user.guest_id,
        "portfolio_id": portfolio.id,
        "cash_balance": portfolio.cash_balance
    }

def get_guest_portfolio(
    db: Session,
    x_guest_id: str | None = Header(default=None)
):
    if not x_guest_id:
        raise HTTPException(
            status_code=400,
            detail="X-Guest-ID header is required"
        )

    user = (
        db.query(User)
        .filter(User.guest_id == x_guest_id.strip())
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Guest session not found"
        )

    portfolio = (
        db.query(Portfolio)
        .filter(Portfolio.user_id == user.id)
        .first()
    )

    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    return portfolio

@app.get("/market/status")
def market_status():
    return {
        "market_open": is_market_open(),
        "timezone": "Asia/Kolkata"
    }


@app.get("/broker/zerodha/connect")
def zerodha_connect(x_guest_id: str | None = Header(default=None)):
    if not x_guest_id or not x_guest_id.strip():
        raise HTTPException(status_code=400, detail="X-Guest-ID header is required")
    try:
        return {"login_url": ZerodhaService.create_login_url(x_guest_id.strip())}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/broker/zerodha/callback")
def zerodha_callback(
    request_token: str | None = None,
    state: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    if status != "success" or not request_token or not state:
        return RedirectResponse(ZerodhaService.callback_url("error", "Login was cancelled"))
    try:
        ZerodhaService.complete_login(db, request_token, state)
        return RedirectResponse(ZerodhaService.callback_url("connected"))
    except (RuntimeError, ValueError) as exc:
        return RedirectResponse(ZerodhaService.callback_url("error", str(exc)))


@app.get("/broker/zerodha/status")
def zerodha_status(
    x_guest_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not x_guest_id or not x_guest_id.strip():
        raise HTTPException(status_code=400, detail="X-Guest-ID header is required")
    return ZerodhaService.connection_status(db, x_guest_id.strip())


@app.post("/broker/zerodha/order/preview")
def zerodha_order_preview(
    request: ZerodhaOrderPreviewRequest,
    x_guest_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not x_guest_id or not x_guest_id.strip():
        raise HTTPException(status_code=400, detail="X-Guest-ID header is required")
    if not is_market_open():
        raise HTTPException(status_code=409, detail="Market is closed")
    return ZerodhaService.preview_order(
        db=db,
        guest_id=x_guest_id.strip(),
        symbol=request.symbol,
        side=request.side,
        quantity=request.quantity,
        price=request.reference_price,
    )


@app.post("/broker/zerodha/order")
def zerodha_order(
    request: ZerodhaOrderRequest,
    x_guest_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not x_guest_id or not x_guest_id.strip():
        raise HTTPException(status_code=400, detail="X-Guest-ID header is required")
    if not is_market_open():
        raise HTTPException(status_code=409, detail="Market is closed")
    return ZerodhaService.execute_order(
        db=db,
        guest_id=x_guest_id.strip(),
        preview_id=request.preview_id,
        idempotency_key=request.idempotency_key,
        confirmed=request.confirmed,
    )


@app.get("/broker/zerodha/orders/{order_id}")
def zerodha_order_status(
    order_id: int,
    x_guest_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not x_guest_id or not x_guest_id.strip():
        raise HTTPException(status_code=400, detail="X-Guest-ID header is required")
    user = db.query(User).filter(User.guest_id == x_guest_id.strip()).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order = db.query(BrokerOrder).filter(
        BrokerOrder.id == order_id,
        BrokerOrder.user_id == user.id,
    ).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return ZerodhaService.order_status(db, x_guest_id.strip(), order)

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

    try:
        return MarketDataService.get_latest_stock_data(symbol)
    except HTTPException:
        raise
    except Exception as exc:
        print(f"[MARKET] Stock data unavailable for {symbol}: {exc}")
        raise HTTPException(
            status_code=503,
            detail="Market data is temporarily unavailable",
        ) from exc


@app.get("/signal/{symbol}")
def signal(symbol: str, db: Session = Depends(get_db)):
    if not symbol or len(symbol) < 2:
        raise HTTPException(status_code=400, detail="Invalid stock symbol")

    try:
        df = MarketDataService.get_historical_data(symbol)
        df = IndicatorService.add_moving_averages(df)
        df = IndicatorService.add_rsi(df)
    except HTTPException:
        raise
    except Exception as exc:
        print(f"[SIGNAL] Data unavailable for {symbol}: {exc}")
        raise HTTPException(
            status_code=503,
            detail="Signal data is temporarily unavailable",
        ) from exc

    try:
        news_insights = NewsService.build_insight(db, symbol)
    except Exception as exc:
        print(f"[NEWS] Signal request continuing without news insights: {exc}")
        news_insights = {
            "status": "UNAVAILABLE",
            "message": "News insights are temporarily unavailable"
        }
    signal_data = SignalService.generate_signal(df, news_insights)
    latest = df.iloc[-1]

    def optional_number(value):
        return None if pd.isna(value) else round(float(value), 2)

    return {
        "symbol": symbol.upper(),
        "current_price": optional_number(latest["Close"]),
        "ma_20": optional_number(latest["MA20"]),
        "ma_50": optional_number(latest["MA50"]),
        "rsi": optional_number(latest["RSI"]),
        **signal_data,
        "news_insights": news_insights
    }

@app.post("/paper-trade/buy")
def paper_buy(
    symbol: str,
    quantity: int,
    x_guest_id: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    portfolio = get_guest_portfolio(db, x_guest_id)

    context = DecisionContextService.build(symbol, db=db)

    rules = context["rules"]
    warnings = None

    if not rules["rules_passed"]:
        warnings = f"Trade executed with rule warnings: {rules['blocked_by']}"

    stock = MarketDataService.get_latest_stock_data(symbol)

    PaperTradeService.buy(
        db=db,
        portfolio_id=portfolio.id,
        symbol=symbol.upper(),
        price=stock["current_price"],
        quantity=quantity
    )

    return {
        "message": "BUY executed",
        "portfolio_id": portfolio.id,
        "rules": rules,
        "warnings": warnings
    }

@app.post("/paper-trade/sell")
def paper_sell(
    symbol: str,
    quantity: int,
    x_guest_id: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    portfolio = get_guest_portfolio(db, x_guest_id)
    context = DecisionContextService.build(symbol, db=db)

    rules = context["rules"]
    warnings = None

    if not rules["rules_passed"]:
        warnings = f"Trade executed with rule warnings: {rules['blocked_by']}"


    stock = MarketDataService.get_latest_stock_data(symbol)

    PaperTradeService.sell(
        db=db,
        portfolio_id=portfolio.id,
        symbol=symbol.upper(),
        price=stock["current_price"],
        quantity=quantity
    )

    return {"message": "SELL executed", "rules": rules, "warnings": warnings}

@app.post("/paper-trade/auto/{symbol}")
def auto_trade(
    symbol: str,
    quantity: int = 1,
    x_guest_id: str | None = Header(default=None),
    db: Session = Depends(get_db)
):

    portfolio = get_guest_portfolio(db, x_guest_id)

    if not is_market_open():
        return {"action": "MARKET CLOSED"}

    symbol = symbol.upper()

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
        portfolio_id=portfolio.id, symbol=symbol
    ).first()

    current_qty = position.quantity if position else 0
    action = "NO ACTION"

    if not rules["rules_passed"]:
        action = f"BLOCKED BY RULES: {rules['blocked_by']}"

    elif signal == "BUY":
        PaperTradeService.buy(
            db=db,
            portfolio_id=portfolio.id,
            symbol=symbol,
            price=price,
            quantity=quantity,
            strategy="auto"
        )
        action = "AUTO BUY EXECUTED"

    elif signal == "SELL" and current_qty > 0:
        PaperTradeService.sell(
            db=db,
            portfolio_id=portfolio.id,
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
def portfolio(
    x_guest_id: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    guest_portfolio = get_guest_portfolio(db, x_guest_id)

    return PaperTradeService.get_portfolio(
        db,
        portfolio_id=guest_portfolio.id
    )

# NEWS INGESTION AND SENTIMENT ANALYSIS ENDPOINTS

@app.post("/news/ingest/{symbol}")
def ingest_news(symbol: str, db: Session = Depends(get_db)):
    return NewsService.ingest_news(db, symbol)

@app.get("/news/insights/{symbol}")
def news_insights(symbol: str, db: Session = Depends(get_db)):
    return NewsService.build_insight(db, symbol)
