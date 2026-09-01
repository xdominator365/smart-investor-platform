# MY DHIRA Tool Analysis

This document captures the current state of the codebase as of the latest changes pushed late last night. It covers the backend architecture, business logic, database model, recent UI/UX updates, and the main product flow of the app.

## 1. Repository status and current scope

Current repo layout:

- [README.md](./README.md)
- [mydhira_deployment.md](./mydhira_deployment.md)
- [smart-investor/backend](./smart-investor/backend)
- [smart-investor/frontend](./smart-investor/frontend)

The product is a paper-trading investment assistant with a financial dashboard, live market data, signal generation, rule-aware trades, and guest-specific portfolio isolation.

The latest commit history shows a concentrated set of feature pushes focused on trading UX, live market integration, and AI signal reliability:

- `9852c26` Use news sentiment in AI signals
- `972273b` Keep AI signals available without news data
- `d3fc334` Fix dynamic stock trend display
- `649a0f2` Connect stock trend to AI indicators
- `561840b` Polish stock search experience
- `0df2d46` Update project documentation
- `586c6f5` Connect dashboard ticker to live market data
- `3d8ebe2` Fix invalid price handling for live stock API
- `16ba001` Add market ticker and terminal trading polish
- `f41b730` Redesign dashboard with premium trading UI
- `5705207` Add portfolio return columns and summary styling
- `01bd639` feat: add guest-based portfolio isolation

This indicates the codebase is moving from a basic prototype toward a more polished live trading terminal with real market data and stronger decision support.

## 2. System architecture

The platform is split into two main runtime layers:

1. Backend: FastAPI service with SQLAlchemy ORM and PostgreSQL
2. Frontend: React + TypeScript + Vite + Tailwind CSS

The app is designed around a paper-trading loop:

- guest user/session creation
- portfolio creation and isolation
- stock data fetch from yfinance
- signal generation from MA/RSI logic
- rules engine gating trades
- execution log storage and dashboard updates
- optional news sentiment overlay

This is consistent with the architecture described in [smart-investor/backend/README.md](./smart-investor/backend/README.md) and the main app docs.

## 3. Backend architecture and core logic

### 3.1 Stack and service structure

Backend files and responsibilities:

- [smart-investor/backend/main.py](./smart-investor/backend/main.py) — FastAPI application entrypoint and route layer
- [smart-investor/backend/database.py](./smart-investor/backend/database.py) — SQLAlchemy engine/session config
- [smart-investor/backend/deps.py](./smart-investor/backend/deps.py) — DB session dependency injection
- [smart-investor/backend/services/market_data_service.py](./smart-investor/backend/services/market_data_service.py) — yfinance-based market data wrapper
- [smart-investor/backend/services/indicator_service.py](./smart-investor/backend/services/indicator_service.py) — moving average and RSI calculations
- [smart-investor/backend/services/signal_service.py](./smart-investor/backend/services/signal_service.py) — BUY/SELL/HOLD decision logic
- [smart-investor/backend/services/paper_trade_service.py](./smart-investor/backend/services/paper_trade_service.py) — cash, position, and trade execution logic
- [smart-investor/backend/services/decision_context_service.py](./smart-investor/backend/services/decision_context_service.py) — rule engine + snapshot context generation
- [smart-investor/backend/services/news_service.py](./smart-investor/backend/services/news_service.py) — sentiment ingestion and insight generation
- [smart-investor/backend/rules](./smart-investor/backend/rules) — rule sets used for trade gating
- [smart-investor/backend/models](./smart-investor/backend/models) — SQLAlchemy table definitions

### 3.2 Database and persistence model

The backend uses PostgreSQL through SQLAlchemy.

Key tables include:

- `users`: guest-based anonymous trading identity
- `portfolios`: user-owned paper portfolio with cash balance
- `positions`: open holdings with quantity and average price
- `trades`: executed buy/sell logs with realized P&L
- `auto_trade_decisions`: rule-based trade decision log
- `ml_feature_snapshot`: feature snapshots used for signal evaluation
- `ml_outcomes`: later outcome labeling for offline ML training
- `news_events`: raw news event sentiment records

Important model files:

- [smart-investor/backend/models/user.py](./smart-investor/backend/models/user.py)
- [smart-investor/backend/models/portfolio.py](./smart-investor/backend/models/portfolio.py)
- [smart-investor/backend/models/position.py](./smart-investor/backend/models/position.py)
- [smart-investor/backend/models/trade.py](./smart-investor/backend/models/trade.py)
- [smart-investor/backend/models/auto_trade_decision.py](./smart-investor/backend/models/auto_trade_decision.py)
- [smart-investor/backend/models/ml_feature_snapshot.py](./smart-investor/backend/models/ml_feature_snapshot.py)
- [smart-investor/backend/models/ml_outcome.py](./smart-investor/backend/models/ml_outcome.py)
- [smart-investor/backend/models/news_event.py](./smart-investor/backend/models/news_event.py)

### 3.3 Session and guest-based portfolio isolation

This is one of the most important recent backend changes.

In [smart-investor/backend/main.py](./smart-investor/backend/main.py):

- `POST /session` accepts a `guest_id`
- the backend looks up or creates a `User` with that guest id
- it creates a default paper portfolio if none exists
- cash balance is initialized to 100000.0

This ensures that multiple browser sessions or users are isolated and do not share positions or trade history.

The frontend sends `X-Guest-ID` on every request and the backend validates it using a helper `get_guest_portfolio()` before allowing portfolio/trade access.

This design is a practical and lightweight alternative to full authentication and is well-suited for a demo/trading sandbox.

### 3.4 Market data handling and live-price robustness

The market data service is built around `yfinance` and is responsible for handling real market data safely.

In [smart-investor/backend/services/market_data_service.py](./smart-investor/backend/services/market_data_service.py):

- `get_latest_stock_data(symbol)` fetches 3 months of historical data
- it strips invalid or NaN closes through `_last_valid_close()`
- it calculates 1D, 5D, and 30D returns using the latest valid close rather than blindly taking the last row
- it raises 404 when no data is available and 422 for invalid price data

This matters because `yfinance` can return final rows with NaN/partial data during closed market phases or inconsistent vendor responses. The fix is a clear production hardening step and directly matches the recent commit `3d8ebe2 Fix invalid price handling for live stock API`.

### 3.5 Indicators and signal creation

Indicator logic lives in:

- [smart-investor/backend/services/indicator_service.py](./smart-investor/backend/services/indicator_service.py)
- [smart-investor/backend/services/signal_service.py](./smart-investor/backend/services/signal_service.py)

The app computes:

- MA20 and MA50 using rolling means
- RSI 14 using standard average-gain/average-loss logic
- RSI slope (`RSI_SLOPE`) for momentum confirmation
- ATR and volume ratio in the decision-context stage

Signal generation rules:

- BUY if MA20 > MA50 and RSI < 70
- SELL if MA20 < MA50 and RSI > 30
- HOLD if trend is blurry or momentum is not aligned
- news sentiment can override the signal when it is highly contradictory

The final signal is returned with a confidence score and a reason string.

### 3.6 Rule engine and trade gating

The trading rules are deterministic and intentionally simple.

Files:

- [smart-investor/backend/rules/rule_engine.py](./smart-investor/backend/rules/rule_engine.py)
- [smart-investor/backend/rules/trend_rules.py](./smart-investor/backend/rules/trend_rules.py)
- [smart-investor/backend/rules/momentum_rules.py](./smart-investor/backend/rules/momentum_rules.py)
- [smart-investor/backend/rules/volume_rules.py](./smart-investor/backend/rules/volume_rules.py)
- [smart-investor/backend/rules/volatility_rules.py](./smart-investor/backend/rules/volatility_rules.py)

Rule checks:

- trend: price must be above MA20 and MA50
- RSI: must be below 70 and rising, otherwise blocked as overbought/weak
- volume: must be at least 1.5x average volume
- volatility: ATR percent must be below 3% to avoid unstable entries

The rule engine returns:

- `rules_passed`
- `risk_level`
- `blocked_by`
- `explanations`
- individual rule flags for trend, RSI, volume, and volatility

This is the core logic behind `POST /paper-trade/buy`, `POST /paper-trade/sell`, and `POST /paper-trade/auto/{symbol}`.

### 3.7 Portfolio execution logic

Paper trading logic is implemented in [smart-investor/backend/services/paper_trade_service.py](./smart-investor/backend/services/paper_trade_service.py).

Core mechanics:

- `buy()` checks sufficient cash, creates or updates `Position`, reduces cash, and logs a BUY trade
- `sell()` checks quantity availability, computes P&L versus average cost, increases cash, removes zero-quantity positions, and logs a SELL trade
- `get_portfolio()` returns cash balance, holdings, realized P&L, total holdings value, and trade history

This is what powers the dashboard summary and holdings grid.

### 3.8 Auto-trade flow

The trading decision flow in [smart-investor/backend/main.py](./smart-investor/backend/main.py) works as follows:

1. Get portfolio for the guest user
2. Check if market is open using `is_market_open()`
3. Build feature vector from recent price history
4. Run rule engine
5. Generate current signal from MA/RSI logic
6. Decide whether to buy or sell
7. Persist `AutoTradeDecision`

The auto-trade route is intentionally conservative:

- if rules fail, it returns `BLOCKED BY RULES`
- if signal is BUY, it executes a buy order with `strategy="auto"`
- if signal is SELL and the user already owns quantity, it sells the full position
- otherwise it does nothing and records the decision

This is useful for explainability and for tracking model decisions in the UI.

### 3.9 News intelligence and sentiment overlay

News services are implemented in [smart-investor/backend/services/news_service.py](./smart-investor/backend/services/news_service.py).

Functionality:

- fetches latest financial news from Marketaux API
- calculates sentiment using `TextBlob` polarity
- stores each article in `news_events`
- aggregates 24h and 7d sentiment
- builds a human-readable insight object with label, trend, attention, and risk flags

Important logic:

- `build_insight()` will auto-ingest if data is missing/stale
- `avg_24h` and `avg_7d` are combined to create a news bias
- the signal service can override a BUY/SELL decision when sentiment contradicts the technical setup

This integration is exactly what the latest commit `9852c26 Use news sentiment in AI signals` refers to. The code also contains graceful fallback behavior when the API key is unavailable, which is crucial for resilience.

### 3.10 ML feature snapshots and offline labeling pipeline

The backend includes a machine-learning-oriented data pipeline beyond the direct live app flow.

Relevant files:

- [smart-investor/backend/jobs/label_outcomes.py](./smart-investor/backend/jobs/label_outcomes.py)
- [smart-investor/backend/scripts/export_ml_data.py](./smart-investor/backend/scripts/export_ml_data.py)
- [smart-investor/backend/scripts/run_labeling_job.py](./smart-investor/backend/scripts/run_labeling_job.py)

The flow is:

- `DecisionContextService.build()` stores a feature snapshot into `ml_feature_snapshot`
- labeling job examines future market movement and assigns `SUCCESS`, `FAILURE`, or `NEUTRAL`
- data can later be exported to CSV for model training

This is a strong sign that the current codebase is designed with a future ML feature store and research workflow in mind.

## 4. API surface overview

The backend exposes these main routes from [smart-investor/backend/main.py](./smart-investor/backend/main.py):

- `POST /session` — create guest user + default portfolio
- `GET /market/status` — return market open/closed for Asia/Kolkata
- `GET /stock/{symbol}` — latest price, OHLCV, and return values
- `GET /signal/{symbol}` — technical signal with MA20, MA50, RSI, and news insight
- `GET /chart/{symbol}` — 3-month chart data for price and indicators
- `POST /paper-trade/buy` — execute BUY trade for guest portfolio
- `POST /paper-trade/sell` — execute SELL trade for guest portfolio
- `POST /paper-trade/auto/{symbol}` — decision and execution based on rules
- `GET /paper-trade/portfolio` — portfolio summary and trade history
- `GET /auto-trade/decisions/{symbol}` — latest auto-trade decision log
- `POST /news/ingest/{symbol}` — ingest and persist news
- `GET /news/insights/{symbol}` — aggregate sentiment for UI and signal overlay

## 5. Frontend architecture and recent code changes

### 5.1 Frontend stack

Frontend stack:

- React 19
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios for API communication
- Recharts for chart rendering

Main files:

- [smart-investor/frontend/package.json](./smart-investor/frontend/package.json)
- [smart-investor/frontend/src/App.tsx](./smart-investor/frontend/src/App.tsx)
- [smart-investor/frontend/src/api.ts](./smart-investor/frontend/src/api.ts)
- [smart-investor/frontend/src/pages/Dashboard.tsx](./smart-investor/frontend/src/pages/Dashboard.tsx)
- [smart-investor/frontend/src/pages/Stocks.tsx](./smart-investor/frontend/src/pages/Stocks.tsx)
- [smart-investor/frontend/src/pages/StockDetail.tsx](./smart-investor/frontend/src/pages/StockDetail.tsx)

### 5.2 API layer and guest session management

The frontend API client in [smart-investor/frontend/src/api.ts](./smart-investor/frontend/src/api.ts) is intentionally simple and production-aware:

- in development it points to `VITE_API_URL` or `http://127.0.0.1:8000`
- in production it uses `/api` to work behind a Vercel proxy
- it stores a `dhira_guest_id` in `localStorage`
- every request automatically adds the `X-Guest-ID` header

This allows the app to maintain a stable anonymous trading identity while allowing guest portfolio isolation.

### 5.3 Routing and navigation

The app uses client-side routing:

- `/` → Dashboard
- `/stocks` → Stock lookup page
- `/stocks/:symbol` → Stock detail and trading terminal

This is defined in [smart-investor/frontend/src/App.tsx](./smart-investor/frontend/src/App.tsx).

### 5.4 Premium trading dashboard redesign

The latest UI work is very visible in:

- [smart-investor/frontend/src/components/Header.tsx](./smart-investor/frontend/src/components/Header.tsx)
- [smart-investor/frontend/src/components/PortfolioSummary.tsx](./smart-investor/frontend/src/components/PortfolioSummary.tsx)
- [smart-investor/frontend/src/components/PortfolioHoldingsTable.tsx](./smart-investor/frontend/src/components/PortfolioHoldingsTable.tsx)
- [smart-investor/frontend/src/components/TradeHistoryTable.tsx](./smart-investor/frontend/src/components/TradeHistoryTable.tsx)

Highlights from the redesign:

- premium dark/light trading terminal styling
- sticky header with market ticker
- status badge for open/closed market
- glowing indicator chips, gradient cards, and animated market signals
- card-based portfolio metrics with mini performance sparklines
- weighted returns and total-return summary controls top-level summary cards

This matches the recent commit history around `premium trading UI`, `market ticker`, and `portfolio return columns`.

### 5.5 Dashboard behavior

[smart-investor/frontend/src/pages/Dashboard.tsx](./smart-investor/frontend/src/pages/Dashboard.tsx) loads the guest portfolio and then:

- fetches latest prices for each holding using `/stock/{symbol}`
- computes weighted portfolio return by invested capital
- refreshes prices every 10s when the market is open
- polls market status every 60s

The result is a live portfolio dashboard with summary metrics and return numbers, instead of static portfolio cards.

### 5.6 Stock detail and terminal experience

The stock detail page in [smart-investor/frontend/src/pages/StockDetail.tsx](./smart-investor/frontend/src/pages/StockDetail.tsx) is where the trading app’s main interaction layer is built.

It loads:

- stock quote and market return fields
- signal data
- chart data
- recent auto-trade decisions
- news insight data

It also provides controls for:

- manual BUY
- manual SELL
- auto-trade evaluation
- quantity selection
- market-open gating

This page is a concise but complete trading terminal.

### 5.7 Key UI components

Important components:

- [smart-investor/frontend/src/components/StockCard.tsx](./smart-investor/frontend/src/components/StockCard.tsx) — stock snapshot with live price and trend tag
- [smart-investor/frontend/src/components/SignalCard.tsx](./smart-investor/frontend/src/components/SignalCard.tsx) — signal banner, confidence bar, explanation text
- [smart-investor/frontend/src/components/NewsInsightsCard.tsx](./smart-investor/frontend/src/components/NewsInsightsCard.tsx) — sentiment summary and risk flags
- [smart-investor/frontend/src/components/PaperTradePanel.tsx](./smart-investor/frontend/src/components/PaperTradePanel.tsx) — buy/sell/auto-trade actions
- [smart-investor/frontend/src/components/AutoTradeExplainability.tsx](./smart-investor/frontend/src/components/AutoTradeExplainability.tsx) — decision log for debugging/explainability
- [smart-investor/frontend/src/components/Charts/PriceChart.tsx](./smart-investor/frontend/src/components/Charts/PriceChart.tsx) — MA20/MA50 overlay on price data
- [smart-investor/frontend/src/components/Charts/RsiChart.tsx](./smart-investor/frontend/src/components/Charts/RsiChart.tsx) — RSI chart

### 5.8 Search and market ticker updates

The search experience was polished in the recent commits:

- [smart-investor/frontend/src/pages/Stocks.tsx](./smart-investor/frontend/src/pages/Stocks.tsx)
- [smart-investor/frontend/src/components/Header.tsx](./smart-investor/frontend/src/components/Header.tsx)

The app includes:

- a dedicated stock scanner page
- search field with uppercase normalization
- market ticker showing NIFTY 50, SENSEX, key stocks, BTC/USD, and GOLD
- real-time market status polling
- market-open/market-closed indicators

This creates a much more terminal-like trading experience than a simple dashboard.

### 5.9 Frontend theming and responsiveness

The design includes a dark/light trading UI and responsive card layout. The theme toggle is implemented in:

- [smart-investor/frontend/src/components/ThemeToggle.tsx](./smart-investor/frontend/src/components/ThemeToggle.tsx)

This supports the premium terminal experience and improves usability in both day and night trading sessions.

## 6. Recent functional improvements and what changed last night

From the commit list and code changes, the most important functional progress includes:

1. Guest isolation
   - unique browser ID and isolated portfolios
   - default 100k paper cash

2. Live market data integration
   - dashboard ticker now pulls from real market data
   - live market status from Asia/Kolkata timezone

3. Price robustness and invalid data handling
   - fix for NaN/invalid `Close` values from yfinance
   - safety checks before using market data for signal generation

4. Premium dashboard redesign
   - better layout, typography, cards, glows, and gradient styling
   - improved stock and portfolio summary presentation

5. Portfolio analytics upgrade
   - return columns for 1D/5D/30D
   - weighted returns and performance summary cards

6. News-aware AI signals
   - sentiment-aware signal logic
   - graceful degradation when news API is unavailable

7. Trade explainability
   - auto-trade decision logs are surfaced to UI
   - users can understand why the system executed or blocked

## 7. Strengths of the current codebase

- Clear separation between API, services, rules, and models
- Good use of SQLAlchemy for structured persistence
- Real market data integration without hardcoded values only
- Reasonable guest-session model for demo sandbox trading
- Strong UI polish for a prototype/product-lite trading dashboard
- Explainable trade logic, not just opaque AI output
- The backend was intentionally built with an ML/data science extension path

## 8. Current gaps and risks

There are also a few important limitations to note:

1. The rule engine is intentionally simple and deterministic, but not yet a robust strategy engine
2. The app still depends on a browser guest identity rather than real auth
3. Some trade safeguards are model-side only; there is no advanced risk manager, slippage logic, or broker integration
4. News and market services can fail separately, but the app mostly handles that with fallback behavior
5. The dashboard still uses a front-end derived portfolio summary and calculations, which are lightweight but not a full financial ledger model
6. The production deployment architecture exists, but the repo is still closer to a demo/learning product than a hardened brokerage platform

## 9. Overall assessment

The codebase is in a strong functional state for a live demo or MVP paper-trading app. The latest set of commits significantly improved the platform from a basic signal dashboard into a more coherent and polished trading terminal.

The most valuable work is the combination of:

- live market data integration
- guest portfolio isolation
- signal + rule engine
- dashboard UX upgrades
- news sentiment overlay

This is a solid foundation for future growth toward a more serious AI investment platform, especially if the team later adds:

- proper authentication
- real execution adapters
- multi-user portfolio management
- strategy backtesting
- stronger ML model training pipelines

## 10. Bottom line

As of the latest pushed changes, the app is a real, working, end-to-end paper-trading dashboard with backend logic, live signal generation, and a premium frontend experience. The repository is no longer just a prototype; it has a clear product shape and a well-structured architecture that can scale into a more advanced investment platform.
