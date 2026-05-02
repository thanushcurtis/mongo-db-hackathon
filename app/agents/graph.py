"""
app/agents/graph.py — Graph Definition
=======================================
Compiles the StateGraph with persistence using MongoDBSaver.
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.mongodb import MongoDBSaver
from app.database import MONGO_URI, DB_NAME, client
from app.agents.state import PortfolioState
from app.agents.nodes import manager_node, research_node, trend_node, synthesize_node

def should_continue(state: PortfolioState) -> str:
    """Router: End if no portfolio found, else research."""
    if not state.get("portfolio"): return "end"
    return "research"

# Create Graph
builder = StateGraph(PortfolioState)
builder.add_node("manager", manager_node)
builder.add_node("research", research_node)
builder.add_node("trend", trend_node)
builder.add_node("synthesize", synthesize_node)

builder.set_entry_point("manager")
builder.add_conditional_edges("manager", should_continue, {"research": "research", "end": END})
builder.add_edge("research", "trend")
builder.add_edge("trend", "synthesize")
builder.add_edge("synthesize", END)

# Compile with MongoDB Checkpointer
checkpointer = MongoDBSaver(client=client, db_name=DB_NAME)
graph = builder.compile(checkpointer=checkpointer)
