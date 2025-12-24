# 🧠 Local Setup Guide – Smart Investor Platform  
### *My Dhira – Data-driven Holistic Intelligent Risk-Aware Algorithms*

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