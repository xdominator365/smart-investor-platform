# 🧭 Architecture Overview – DHIRA  
### *Data-driven Holistic Intelligent Risk-Aware Algorithms*

This document provides a detailed overview of the **system architecture** for the Smart Investor Platform.  
The design emphasizes modularity, scalability, and clean separation between frontend and backend layers.

## Current Product Scope

DHIRA is a paper-trading investment assistant with a React trading dashboard and a FastAPI service. The current experience includes:

- Live market prices and 1-day, 5-day, and 30-day return percentages powered by `yfinance`.
- Guest-based portfolio isolation using the `X-Guest-ID` request header.
- Portfolio holdings, current value, P&L, and weighted period-return summaries.
- BUY, SELL, and rule-aware auto-trade paper execution.
- Technical signals using MA20, MA50, RSI, volume, volatility, and news insights.
- A dark/light trading-terminal interface with a live ticker strip, animated return states, and performance sparklines.

## Recent Implementation Changes

Recent work from August 13 through September 1, 2026 includes:

- Added Render deployment configuration, a Vercel API proxy, and single-page-app routing.
- Added browser guest sessions with isolated portfolios and a default paper-trading balance.
- Added portfolio 1D/5D/30D return columns, total-return summaries, and green/red profit-loss states.
- Redesigned the dashboard with a premium trading-terminal layout, dark/light theme support, motion, and responsive cards.
- Added a live market ticker and return-driven mini performance charts.
- Fixed invalid `yfinance` final rows by selecting the latest valid close when market data contains `NaN` values.

---

## 🏗️ 1. High-Level Design

The platform follows a **modular, service-oriented architecture (SOA)** where each component handles a specific domain responsibility.

- **Frontend** and **Backend** are completely **decoupled**.
- Communication occurs through well-defined **REST APIs**.
- Designed for **scalability**, **observability**, and **performance**.

---

## ⚙️ 2. Backend Architecture

### 🧰 Stack
- **FastAPI** — High-performance Python web framework for APIs.  
- **PostgreSQL** — Primary relational database for transactional and analytic data.  
- **SQLAlchemy** — ORM for modeling and query abstraction.  
- **Alembic** — Handles schema migrations and version control for the database.

### 🔑 Core Principles
- Backend serves as the **single source of truth**.  
- APIs are **stateless** and **idempotent**.  
- All trade activities are recorded in **append-only logs**.  
- **Deterministic auto-trading rules** ensure reproducibility of decisions.  

### 📂 Core Modules
```
backend/
├── services/     # Core business logic (trading, analytics, etc.)
├── rules/        # Trend, momentum, volume, and volatility rules
├── models/       # ORM models and schema definitions
├── alembic/      # Database migrations
├── utils/        # Helper and utility functions
└── main.py       # Application entry point
```

---

## 💻 3. Frontend Architecture

### 🧰 Stack
- **React** — Component-driven UI library.  
- **TypeScript** — Strong typing for maintainability and reliability.  
- **Tailwind CSS** — Utility-first styling for consistent design.  
- **React Router** — Enables client-side routing and navigation.

### 🔑 Core Principles
- **Page-based routing** for clear user navigation.  
- **Backend-driven state**, keeping frontend lightweight and reactive.  
- **Persistent theming** for dark/light modes.  
- **Market-aware refresh logic** — UI updates align with live market status.

### 📁 Structure
```
frontend/
├── src/
│   ├── components/   # Reusable UI components
│   ├── pages/        # Page-based views
│   ├── hooks/        # Custom React hooks
│   ├── context/      # State management and context providers
│   ├── styles/       # Tailwind and theme configs
│   └── utils/        # Frontend utilities
└── package.json
```

---

## 🔄 4. Trading Flow

A simplified overview of the trading decision cycle:

1. **User selects a stock** from the UI.  
2. **Backend computes key indicators** (MA20, MA50, RSI, volume, and volatility) from live market data.
3. **Signal is generated** (Buy/Sell/Hold).  
4. **Auto-trade engine** evaluates deterministic trading rules.  
5. **Decision is logged** in the trade and auto-trade decision records (either executed or blocked).
6. **UI instantly reflects** the decision and updates portfolio state.

```
User → Frontend → Backend → Signal Engine → Trade Rules → Logs → Frontend Update
```

---

## 🗃️ 5. Data Model (Simplified)

Key relational entities that form the backbone of the trading system:

| Table | Description |
|--------|--------------|
| **portfolios** | User-specific holdings and asset allocations. |
| **positions** | Current open positions with metadata like entry time and size. |
| **trades** | Historical trade actions and executions. |
| **auto_trade_decisions** | Logs of automated trading logic evaluations. |

---

## 🔌 6. API Surface

The backend exposes these primary routes. Portfolio and trade routes require an `X-Guest-ID` header created by the frontend session flow.

| Route | Purpose |
|---|---|
| `POST /session` | Create or restore a guest user and paper portfolio. |
| `GET /market/status` | Return market-open status and the `Asia/Kolkata` timezone. |
| `GET /stock/{symbol}` | Return the latest price, OHLCV data, and 1D/5D/30D returns. |
| `GET /signal/{symbol}` | Return technical indicators and BUY/SELL/HOLD signal data. |
| `GET /chart/{symbol}` | Return historical prices with MA20, MA50, and RSI values. |
| `GET /paper-trade/portfolio` | Return the current guest portfolio and trade history. |
| `POST /paper-trade/buy` / `POST /paper-trade/sell` | Execute paper trades at the latest market price. |
| `POST /paper-trade/auto/{symbol}` | Evaluate rules and execute an automated paper trade when the market is open. |
| `GET /auto-trade/decisions/{symbol}` | Return recent automated-trade decisions. |
| `POST /news/ingest/{symbol}` / `GET /news/insights/{symbol}` | Ingest and retrieve news sentiment insights. |

The production frontend sends `/api` requests through the Vercel rewrite to the Render backend. Local development uses `VITE_API_URL` or `http://127.0.0.1:8000`.

## 🔮 7. Future Extensions

Planned architectural enhancements to expand system intelligence and scale:

- **ML Feature Store** — For real-time predictive modeling.  
- **Backtesting Engine** — To simulate strategies on historical data.  
- **Strategy Experimentation Module** — For fast A/B testing of trading algorithms.  
- **Multi-user Authentication** — Enhanced auth and role-based access.  
- **Broker Integrations** — Support for live order execution via multiple brokers (e.g., Zerodha, AngelOne, Upstox).

---

## Local Setup Guide 

This guide walks you through setting up and running the project locally.  
Each developer runs their **own isolated environment and database**.

---

## 🚀 1. Prerequisites

Before you begin, ensure the following tools are installed on your system:

- **Python** 3.10+
- **Node.js** 18+
- **PostgreSQL** (latest stable version)
- **Git**

You can verify installations using:
```
python --version
node --version
psql --version
git --version
```

---

## 📁 2. Repository Structure

Project directory layout:
```
smart-investor-platform/
├── smart-investor/
│   ├── backend/
│   ├── frontend/
│   ├── backend/README.md
│   └── frontend/README.md
├── README.md
└── *.md                 # setup and deployment documentation
```

---

## 🗄️ 3. PostgreSQL Setup

### 3.1 Start PostgreSQL
Ensure the PostgreSQL service is **running locally**.

### 3.2 Create Database
Run the following command in your PostgreSQL shell or SQL client:
```
CREATE DATABASE ai_investor;
```

---

## ⚙️ 4. Environment Configuration

### 4.1 Create `.env` file
Inside the project folder:

```
cd smart-investor
cp .env.example .env
```

### 4.2 Update `.env`
Edit the `.env` file and update the database URL:

```
DATABASE_URL=postgresql://postgres:<YOUR_PASSWORD>@localhost:5432/ai_investor
```

Replace `<YOUR_PASSWORD>` with your PostgreSQL password.

---

## 🧩 5. Backend Setup

### 5.1 Navigate to backend
```
cd smart-investor/backend
```

### 5.2 Create and activate virtual environment
```
python -m venv .venv
```

**Windows:**
```
.venv\Scripts\activate
```

**Mac/Linux:**
```
source .venv/bin/activate
```

### 5.3 Install dependencies
```
pip install -r requirements.txt
```

### 5.4 Apply database migrations
```
alembic upgrade head
```

### 5.5 Start the backend server
```
uvicorn main:app --reload
```

**Backend runs at:** [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 💻 6. Frontend Setup

### 6.1 Navigate to frontend
```
cd smart-investor/frontend
```

### 6.2 Install dependencies
```
npm install
```

### 6.3 Run the frontend server
```
npm run dev
```

**Frontend runs at:** [http://localhost:5173](http://localhost:5173)

---

## 📊 8. Market Behavior

- **Market hours (IST):** 9:15 AM – 3:30 PM  
- Data **auto-refresh pauses** when the market is closed  
- **Auto-trade feature** is disabled when the market is closed  

When markets are closed, the backend serves the latest valid historical close. The frontend refreshes portfolio prices after loading and when market status changes, then polls holdings every 10 seconds while the market is open. The global ticker refreshes every 45 seconds.

---