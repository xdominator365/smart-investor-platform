# 🧭 Architecture Overview – My DHIRA  
### *Data-driven Holistic Intelligent Risk-Aware Algorithms*

This document provides a detailed overview of the **system architecture** for the Smart Investor Platform.  
The design emphasizes modularity, scalability, and clean separation between frontend and backend layers.

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
├── api/          # Route definitions and request handling
├── services/     # Core business logic (trading, analytics, etc.)
├── models/       # ORM models and schema definitions
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
2. **Backend computes key indicators** (RSI, MACD, etc.) from live market data.  
3. **Signal is generated** (Buy/Sell/Hold).  
4. **Auto-trade engine** evaluates deterministic trading rules.  
5. **Decision is logged** in the `trade_log` (either executed or blocked).  
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

## 🔮 6. Future Extensions

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
│   ├── .env.example
│   └── README.md
└── docs/
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

## 📊 7. Market Behavior

- **Market hours (IST):** 9:15 AM – 3:30 PM  
- Data **auto-refresh pauses** when the market is closed  
- **Auto-trade feature** is disabled when the market is closed  

---