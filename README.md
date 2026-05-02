# Personal Portfolio AI Advisor - Backend

An agentic AI system built with **LangGraph**, **MongoDB Atlas**, and **Cohere** to provide personalized financial analysis and portfolio recommendations.

## 🚀 Overview

This backend system leverages a multi-node agent graph to:
1. **Manager Node**: Retrieve and hydrate user profiles and portfolio data from MongoDB.
2. **Research Node**: Perform concurrent RAG-based research on every stock in a user's portfolio using yfinance and MongoDB Atlas Vector Search (Voyage AI embeddings).
3. **Trend Node**: Aggregate technical signals and platform-wide trending stocks.
4. **Synthesis Node**: Generate a comprehensive, personalized Markdown report using Cohere's Command-R+.

## 🛠 Tech Stack

- **Framework**: FastAPI
- **Orchestration**: LangGraph (StateGraph)
- **Database**: MongoDB Atlas (Vector Search & Persistence)
- **LLM**: Cohere (command-r-plus-08-2024)
- **Embeddings**: Voyage AI (voyage-finance-2)
- **Data Source**: Yahoo Finance (yfinance)

## 📡 API Documentation for Frontend

The backend runs by default on `http://localhost:8000`.

### 1. Portfolio Analysis
**Endpoint:** `POST /analyze/{user_id}`

Runs the full analysis graph for a specific user.

- **URL Params:** `user_id` (e.g., `hardcoded_user_1`)
- **Response:**
  ```json
  {
    "report": "# Personalized Financial Report for Thanush..."
  }
  ```

### 2. Chat-Driven Analysis
**Endpoint:** `POST /chat`

Allows users to ask specific questions about their portfolio.

- **Request Body:**
  ```json
  {
    "user_id": "hardcoded_user_1",
    "message": "Should I be worried about my Apple holdings?"
  }
  ```
- **Response:**
  ```json
  {
    "report": "Based on recent news and trends for AAPL..."
  }
  ```

### 3. Health Check
**Endpoint:** `GET /health`

- **Response:** `{"status": "healthy"}`

---

## ⚙️ Local Setup

1. **Environment Variables**: Create a `.env` file with:
   ```env
   MONGO_URI=your_mongodb_atlas_uri
   COHERE_API_KEY=your_cohere_key
   VOYAGE_API_KEY=your_voyage_key
   ```

2. **Conda Environment**:
   ```bash
   conda activate portfolio-agent
   pip install -r requirements.txt
   ```

3. **Run Backend**:
   ```bash
   python main.py
   ```

## 🏗 Graph Architecture

The system uses a stateful graph with MongoDB checkpointers to maintain thread history:

```text
Manager -> Intent Router -> Research (Sequential) -> Trend -> Synthesize -> END
```

Each step updates a shared `PortfolioState` which is persisted across turns in MongoDB.

---

## 🎨 Frontend UI (Vite + React)

The project includes a modern React dashboard located in the `/portfolio-ui` directory.

### Setup & Run UI

1. **Navigate to directory**:
   ```bash
   cd portfolio-ui
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Run Development Server**:
   ```bash
   npm run dev
   ```

The dashboard will be available at `http://localhost:5173`. Make sure the Backend is running on port 8000 for the UI to fetch data correctly.

