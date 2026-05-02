"""
main.py — FastAPI Backend Entry Point
======================================
Serves the Agentic Portfolio API.
"""

import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.database import get_user_profile
from app.agents.graph import graph

app = FastAPI(title="Personal Portfolio AI Advisor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str = "hardcoded_user_1"
    message: str

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
    """Chat-driven analysis."""
    config = {"configurable": {"thread_id": f"chat_{uuid.uuid4().hex[:6]}"}}
    initial_state = {"user_id": request.user_id, "chat_message": request.message}
    result = graph.invoke(initial_state, config=config)
    return {"report": result.get("final_report", "Error")}

@app.get("/health")
def health(): return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
