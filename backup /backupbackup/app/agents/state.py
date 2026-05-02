"""
app/agents/state.py — State Definition
=======================================
TypedDict defining the shared state for the LangGraph agents.
"""

from typing import TypedDict

class PortfolioState(TypedDict):
    """Shared state between all nodes in the graph."""
    # Input
    user_id: str
    chat_message: str            # Optional user question
    
    # Context (populated by Manager)
    user_name: str
    risk_tolerance: str
    portfolio: list[dict]        # [{ticker, shares, buy_price}, ...]
    
    # Results
    research_results: dict       # {ticker: analysis}
    trend_results: dict          # {ticker: trend_summary}
    market_trends: str           # Hot stocks + platform social signal
    
    # Final Synthesis
    final_report: str            # Markdown output
