# AI Investor

An AI-powered paper trading application that provides:
- Buy/Sell/Hold signals
- Technical indicators (MA, RSI)
- Paper trading with P&L
- Portfolio & trade history
- Auto-trading logic

## Architecture
- FastAPI backend with PostgreSQL
- React + Tailwind frontend
- Service-oriented backend design

## Setup

### Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

### Frontend
cd frontend
npm install
npm run dev





