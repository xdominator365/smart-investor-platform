## Backend Developer Guide

The backend is a FastAPI service for market data, technical signals, paper trading, news insights, and user-confirmed Zerodha live-order execution. The application is intentionally split into recommendation, preview, confirmation, and broker-execution stages:

```text
Market data -> indicators -> BUY/SELL/HOLD signal -> user preview -> explicit confirmation -> Zerodha
```

An AI signal never places a live order by itself. `HOLD` cannot create a live order preview.

### Local setup

From `smart-investor/backend`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

The API listens on `http://127.0.0.1:8000`. The frontend normally runs on `http://localhost:5173`.

### Environment variables

Create the ignored file `smart-investor/backend/.env` for local development. Never commit it or place secrets in frontend code.

| Variable | Required | Purpose | Where to configure |
|---|---:|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string used by SQLAlchemy and Alembic. | Local `backend/.env`; Render service environment. |
| `KITE_API_KEY` | Yes for Zerodha | Zerodha Kite Connect app/client ID used to create the login URL. | Local `backend/.env`; Render service environment. |
| `KITE_API_SECRET` | Yes for Zerodha callback | Server-only secret used to exchange the Zerodha request token. | Local `backend/.env`; Render service environment. |
| `BROKER_TOKEN_ENCRYPTION_KEY` | Yes before login completion | Fernet key used to encrypt Zerodha access tokens at rest. Generate with `Fernet.generate_key()`. Keep stable. | Local `backend/.env`; Render service environment. |
| `FRONTEND_URL` | Recommended | Redirect target after Zerodha login, for example `http://localhost:5173`. | Local `backend/.env`; Render service environment. |
| `MARKETAUX_API_KEY` | Optional | News ingestion API key. Signals still work if news is unavailable. | Local `backend/.env`; Render service environment. |
| `REDIS_URL` | Optional | Redis Pub/Sub fan-out for multiple backend instances. | Local `backend/.env`; Render service environment. |
| `PYTHON_VERSION` | Deployment | Render Python version, currently configured in `render.yaml`. | Render configuration. |

Example local configuration, with secret values omitted:

```env
DATABASE_URL=postgresql://user:password@host/database
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret
BROKER_TOKEN_ENCRYPTION_KEY=your_fernet_key
FRONTEND_URL=http://localhost:5173
MARKETAUX_API_KEY=your_marketaux_key
REDIS_URL=redis://localhost:6379/0
```

### Zerodha setup

Create a Kite Connect app at `https://developers.kite.trade/create`. Configure the callback URL to:

```text
http://localhost:8000/broker/zerodha/callback
```

For production, use the public backend URL instead. The frontend must use the matching backend URL through `VITE_API_URL` and `VITE_WS_URL`.

The connection flow is:

1. The frontend calls `GET /broker/zerodha/connect` with `X-Guest-ID`.
2. The backend creates a short-lived, single-use state and returns a Kite login URL.
3. Zerodha redirects to `GET /broker/zerodha/callback`.
4. The backend exchanges the request token using `KITE_API_SECRET`.
5. The access token is encrypted with `BROKER_TOKEN_ENCRYPTION_KEY` and stored in `broker_accounts`.
6. The frontend reads only connection status; access tokens are never returned.

### Live order flow

The live order flow is intentionally fail-closed:

1. `POST /broker/zerodha/order/preview` validates the connection, market hours, side, quantity, price, and symbol mapping. It returns a five-minute `preview_id`.
2. The user reviews the symbol, side, quantity, exchange, product, order type, and estimated value.
3. The browser asks for explicit confirmation and sends `POST /broker/zerodha/order` with `preview_id`, a unique `idempotency_key`, and `confirmed: true`.
4. The backend verifies the preview, token, market status, and broker account.
5. BUY orders validate available Zerodha equity funds. SELL orders validate NSE holdings.
6. A `SUBMITTING` audit row is committed before the broker request.
7. The broker order is submitted. The audit row becomes `OPEN` or `REJECTED`.
8. `GET /broker/zerodha/orders/{order_id}` refreshes status from Zerodha order history when possible.

Never bypass the preview endpoint or reuse an idempotency key for a different order. The order audit is stored in `broker_orders`.

### API routes

| Route | Purpose |
|---|---|
| `POST /session` | Create or recover a guest paper-trading session. |
| `GET /market/status` | Return market status in Asia/Kolkata. |
| `GET /stock/{symbol}` | Return the latest valid quote and period returns. |
| `GET /signal/{symbol}` | Calculate technical signal and optional news overlay. |
| `GET /chart/{symbol}` | Return historical chart data. |
| `GET /broker/zerodha/connect` | Create a Zerodha login URL. |
| `GET /broker/zerodha/callback` | Exchange the Zerodha request token. |
| `GET /broker/zerodha/status` | Return broker connection status without secrets. |
| `POST /broker/zerodha/order/preview` | Validate and create a temporary order preview. |
| `POST /broker/zerodha/order` | Place a confirmed, audited live Zerodha order. |
| `GET /broker/zerodha/orders/{order_id}` | Return and refresh an audited order status. |
| `GET /paper-trade/portfolio` | Return guest portfolio and paper trades. |
| `POST /paper-trade/buy` / `POST /paper-trade/sell` | Execute paper orders. |
| `POST /paper-trade/auto/{symbol}` | Evaluate a paper auto-trade during market hours. |
| `POST /news/ingest/{symbol}` / `GET /news/insights/{symbol}` | Ingest and read news sentiment. |

### Database migrations

Run migrations after configuring `DATABASE_URL`:

```powershell
alembic upgrade head
alembic current
```

The broker migration creates `broker_accounts` for encrypted sessions and `broker_orders` for order audit/status tracking. Do not edit an already-applied migration; create a new revision.

### Market data limitations

`yfinance.AsyncWebSocket` is used as the primary quote stream. The fallback uses `history(interval="1m")`, which is polling and is not millisecond real-time. yfinance is an unofficial Yahoo client and has no guaranteed latency or uptime SLA. Use an official market-data provider for production trading guarantees.

### Tests and checks

```powershell
python -m pytest tests/test_websocket_market_stream.py -q
python -m compileall -q main.py services models
```

Use mocked Kite responses for order tests. Never run live-order tests against a real account without a deliberate small-quantity test plan.

---

## Signal concepts

Think of stock prices like this:

Price is noisy — it goes up, down, up, down every day
Trend is smooth — the real direction underneath the noise

A moving average is just a way to smooth out the noise so you can see the trend clearly.

🔹 Simple Analogy (Very Important)

Imagine:

You weigh yourself every day. Daily weight fluctuates due to food, water, etc. Instead of panicking daily, you take:
Average of last 20 days
That average shows your real trend.
Stock prices work the same way.

📌 What does “20-day Moving Average” mean?

Average closing price of the last 20 trading days

Mathematically:
MA20 today = (Price of last 20 days) / 20

Tomorrow:
Oldest day drops out
New day comes in
Average “moves”

➡️ That’s why it’s called moving average.

🔹 Why do we use different periods (20 & 50)?

🟢 Short-term MA (20-day)

* Reacts faster
* Follows recent price changes
* Used by traders

🔵 Long-term MA (50-day)

* Reacts slower
* Shows bigger picture
* Used by investors

So:

* MA20 = recent mood
* MA50 = long-term belief

----------------------------------------------------------------------------------------------------------------------

🧠 How to Interpret Confidence (Very Important)
Confidence	Meaning
0–1%	Very weak signal
1–3%	Moderate
3–6%	Strong
6%+	Very strong (rare)

This feels real, not gimmicky.


----------------------------------------------------------------------------------------------------------------------

🧠 What is RSI (Relative Strength Index)?

RSI answers one simple question:

“Is this stock overbought or oversold?”

It measures momentum, not trend.

📊 RSI Scale (0–100)
RSI Value	Meaning	Action
> 70	Overbought	⚠️ Price may fall
< 30	Oversold	🔥 Price may rise
30–70	Neutral	😐 No strong momentum


🧠 Intuition (Very Important)

RSI does NOT care about price level
It cares about speed of price change
It protects you from:
Buying when price already ran too much
Selling after price already crashed

🔥 Why MA + RSI Together is Powerful

Indicator	What it tells

MA	        Direction (trend)
RSI	        Strength (momentum)

Example:
MA says BUY
RSI = 75 → ❌ Don’t buy (too late)

MA says BUY
RSI = 35 → ✅ Healthy entry

----------------------------------------------------------------------------------------------



## Current Backend Reference

The backend is a FastAPI paper-trading API backed by PostgreSQL, SQLAlchemy, Alembic, and `yfinance`. It serves live market snapshots, technical signals, portfolio operations, auto-trade decisions, charts, and news insights.

### Setup

From `smart-investor/backend`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

Configure `DATABASE_URL` for PostgreSQL before applying migrations. The API listens on `http://127.0.0.1:8000` by default.

### Guest Portfolio Contract

Call `POST /session` with a JSON body containing a non-empty `guest_id`. The returned portfolio is isolated to that guest. Send the same value as `X-Guest-ID` on portfolio and paper-trade requests. The frontend creates and persists this identifier in browser local storage.

### Market Data and Returns

`GET /stock/{symbol}` returns the latest valid close plus OHLCV data and `return_1d`, `return_5d`, and `return_30d` percentages. The service skips invalid or `NaN` closing rows returned by `yfinance`, which is important when the market is closed or a provider returns an incomplete final row. Returns are calculated from valid historical closes over the requested trading-day lookback.

### Main Routes

| Route | Purpose |
|---|---|
| `GET /market/status` | Market status in IST. |
| `GET /stock/{symbol}` | Current quote and period returns. |
| `GET /signal/{symbol}` | Indicators and trading signal. |
| `GET /chart/{symbol}` | Three months of chart and indicator data. |
| `GET /paper-trade/portfolio` | Guest portfolio, holdings, and trade history. |
| `POST /paper-trade/buy` / `POST /paper-trade/sell` | Rule-aware paper execution. |
| `POST /paper-trade/auto/{symbol}` | Market-hours auto-trade evaluation. |
| `GET /auto-trade/decisions/{symbol}` | Recent automated decisions. |
| `POST /news/ingest/{symbol}` / `GET /news/insights/{symbol}` | News ingestion and sentiment insights. |

For deployment, `Procfile` and `render.yaml` configure the Render service. Keep database credentials and other secrets in environment variables rather than source control.



