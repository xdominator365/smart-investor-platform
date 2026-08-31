🧠 What is a Moving Average (MA) — in simple terms

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



