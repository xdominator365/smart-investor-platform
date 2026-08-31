# DHIRA Frontend

The frontend is a React 19, TypeScript, Vite, and Tailwind CSS trading dashboard for the DHIRA paper-trading platform.

## Features

- Dashboard with cash, realized P&L, unrealized P&L, and total P&L.
- Holdings table with current prices, P&L, and weighted 1D/5D/30D returns.
- Live market ticker for indices, equities, Bitcoin, and gold.
- Dynamic green/red return states and performance sparklines driven by API data.
- Stock search and detail views with price charts, moving averages, RSI, signals, news insights, and paper trading.
- Dark/light theme support.

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
```

In production, `/api/*` requests are rewritten by `vercel.json` to the Render backend. The frontend automatically creates a browser guest ID and sends it as `X-Guest-ID` to keep paper portfolios isolated.

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

## Structure

```text
src/
|-- api.ts                 # Axios API client and guest header
|-- App.tsx                # Routes and shared shell
|-- components/            # Header, portfolio, chart, trade, and news UI
`-- pages/                 # Dashboard, Stocks, and StockDetail views
```
