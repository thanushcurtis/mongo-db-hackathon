"""
main.py — FastAPI Backend Entry Point
======================================
Serves the Agentic Portfolio API.
"""

import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.database import get_user_profile, get_all_user_holdings
from app.agents.graph import graph
from app.tools.tools import get_trending_stocks, get_trending_stocks_data

app = FastAPI(title="Personal Portfolio AI Advisor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

class ChatRequest(BaseModel):
    user_id: str = "hardcoded_user_1"
    message: str
    history: List[Dict[str, Any]] = []

@app.get("/portfolio/{user_id}")
async def portfolio(user_id: str):
    """Return user profile and portfolio holdings."""
    profile = get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile

@app.post("/analyze/{user_id}")
async def analyze(user_id: str):
    """Run full portfolio analysis graph."""
    if not get_user_profile(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    config = {"configurable": {"thread_id": f"req_{uuid.uuid4().hex[:6]}"}}
    initial_state = {"user_id": user_id, "chat_message": ""}
    result = graph.invoke(initial_state, config=config)
    return {"report": result.get("final_report", "Error")}

@app.post("/chat")
async def chat(request: ChatRequest):
    """Conversational chat endpoint with portfolio context."""
    profile = get_user_profile(request.user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    from app.agents.nodes import llm
    
    sys_prompt = f"""You are Tiser AI, a conversational financial advisor.
User Profile: {profile.get('name', 'Investor')}, Risk Tolerance: {profile.get('risk_tolerance', 'moderate')}
Portfolio: {profile.get('portfolio', [])}
Answer concisely and conversationally. Do not generate a massive report unless asked. Focus on the user's latest question."""

    langchain_messages = [SystemMessage(content=sys_prompt)]
    
    # Add conversation history
    for msg in request.history:
        if msg.get("role") == "user":
            langchain_messages.append(HumanMessage(content=msg.get("text")))
        elif msg.get("role") == "bot":
            langchain_messages.append(AIMessage(content=msg.get("text")))
            
    # Add the new message
    langchain_messages.append(HumanMessage(content=request.message))
    
    # Generate conversational response
    resp = llm.invoke(langchain_messages)
    return {"report": resp.content}

@app.get("/trending")
async def trending():
    """Return trending stocks data (markdown string)."""
    return {"data": get_trending_stocks.invoke({})}

@app.get("/api/market-trends")
async def market_trends():
    """Return structured market trend data for the UI charts."""
    return {"data": get_trending_stocks_data()}

@app.get("/platform-holdings")
async def platform_holdings():
    """Return aggregated platform-wide holdings."""
    return {"holdings": get_all_user_holdings()}

@app.get("/health")
def health(): return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
