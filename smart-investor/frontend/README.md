# DHIRA Frontend

The frontend is a React 19, TypeScript, Vite, and Tailwind CSS trading dashboard for the DHIRA paper-trading platform.

## Features

- Dashboard with cash, realized P&L, unrealized P&L, and total P&L.
- Holdings table with current prices, P&L, and weighted 1D/5D/30D returns.
- Live market ticker for indices, equities, Bitcoin, and gold.
- Dynamic green/red return states and performance sparklines driven by API data.
- Stock search and detail views with price charts, moving averages, RSI, signals, news insights, and paper trading.
- Dark/light theme support.
- Zerodha connection, signal-aware order preview, and explicit live-order confirmation UI.

## Broker and live-order flow

The frontend never stores Zerodha secrets or access tokens. It sends the browser guest ID through the Axios interceptor and calls the backend broker routes:

1. `GET /broker/zerodha/status` checks whether the current guest is connected.
2. `GET /broker/zerodha/connect` returns a login URL and redirects the browser to Kite.
3. A BUY or SELL signal displays a preview action. HOLD displays no live-order action.
4. `POST /broker/zerodha/order/preview` creates a short-lived preview containing the mapped Zerodha symbol, exchange, quantity, reference price, order type, product, and estimate.
5. The user confirms in the browser before `POST /broker/zerodha/order` is called.
6. The backend performs the final token, market, funds/holdings, idempotency, and audit checks before sending anything to Zerodha.

The frontend does not place an order from an AI signal automatically. The backend remains the source of truth for all safety checks.

## Setup

Requirements: Node.js 18+ and npm.

```powershell
npm install
npm run dev
```

The development server runs at `http://localhost:5173`.

### API Configuration

In local development, requests use `VITE_API_URL` when defined, otherwise `http://127.0.0.1:8000`:

```env
VITE_API_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000/ws/market
```

In production, `/api/*` requests are rewritten by `vercel.json` to the Render backend. The frontend automatically creates a browser guest ID and sends it as `X-Guest-ID` to keep paper portfolios isolated.

`VITE_WS_URL` is important in production because Vercel rewrites REST requests but does not proxy the WebSocket route. Set it to the backend WebSocket endpoint, for example:

```env
VITE_WS_URL=wss://your-backend.onrender.com/ws/market
```

Frontend environment files belong in `smart-investor/frontend/.env.local` for local development and in the Vercel project environment settings for deployment. Do not put `KITE_API_KEY`, `KITE_API_SECRET`, `DATABASE_URL`, or `BROKER_TOKEN_ENCRYPTION_KEY` in frontend variables.

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Start the Vite development server. |
| `npm run build` | Run TypeScript checks and create a production build. |
| `npm run preview` | Preview the production build locally. |

## Refresh Behavior

- Portfolio prices load when the dashboard opens and when market status changes.
- Holdings refresh every 10 seconds while the market is open.
- The global market ticker refreshes every 45 seconds.
- Closed-market responses use the latest valid market close supplied by the backend.
- Stock detail prices also consume the backend market WebSocket. The backend uses yfinance live events first and labels its `1m` fallback as non-realtime.
- Dashboard polling merges successful snapshots into existing state, so a temporary provider failure does not erase the last valid price.

## Production configuration

The backend deployment is configured in `smart-investor/backend/render.yaml`; the frontend REST rewrite is configured in `smart-investor/frontend/vercel.json`. Configure the backend environment variables in Render and the `VITE_*` variables in Vercel. Rebuild the frontend after changing Vite variables because they are embedded at build time.

The backend must have a reachable PostgreSQL database and must run `alembic upgrade head` before the broker connection flow is used. Zerodha requires the callback URL configured in the Kite app to exactly match the deployed backend callback route.

## Validation

```powershell
npm run build
```

This runs TypeScript validation and the Vite production build. Backend tests should be run from `smart-investor/backend` with its `.venv` activated.

## Structure

```text
src/
|-- api.ts                 # Axios API client and guest header
|-- App.tsx                # Routes and shared shell
|-- components/            # Header, portfolio, chart, trade, and news UI
`-- pages/                 # Dashboard, Stocks, and StockDetail views
```
