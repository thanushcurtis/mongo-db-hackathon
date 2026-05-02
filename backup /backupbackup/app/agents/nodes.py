"""
app/agents/nodes.py — Agent Node Logic
=======================================
Implementation of Manager, Research, Trend, and Synthesis nodes.
"""

import os
import concurrent.futures
from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage, SystemMessage
from app.database import get_user_profile
from app.agents.state import PortfolioState
from app.tools import (
    fetch_stock_news, get_stock_price_info, search_market_cache,
    embed_and_store_news, get_trending_stocks, get_platform_popular, get_ticker_details
)

# Initialize LLM
llm = ChatCohere(
    model="command-r-plus-08-2024",
    temperature=0.3,
    cohere_api_key=os.environ.get("COHERE_API_KEY"),
)

def manager_node(state: PortfolioState) -> dict:
    """Reads user profile and hydrates state."""
    profile = get_user_profile(state["user_id"])
    if not profile:
        return {"final_report": "❌ User profile not found."}
    return {
        "user_name": profile.get("name", "Investor"),
        "risk_tolerance": profile.get("risk_tolerance", "moderate"),
        "portfolio": profile.get("portfolio", []),
    }

def _research_single_stock(t: str, risk_tolerance: str) -> tuple[str, str]:
    """Helper to process a single stock concurrently."""
    news = fetch_stock_news.invoke({"ticker": t})
    embed_and_store_news.invoke({"ticker": t, "news_text": news})
    intel = search_market_cache.invoke({"query": f"{t} outlook", "k": 2})
    details = get_ticker_details.invoke({"ticker": t})
    
    prompt = f"Analyze {t} for a {risk_tolerance} investor.\nNews: {news}\nIntel: {intel}\nDetails: {details}"
    resp = llm.invoke([SystemMessage(content="You are a financial analyst."), HumanMessage(content=prompt)])
    return t, resp.content

def research_node(state: PortfolioState) -> dict:
    """Performs RAG-based research for each ticker in the portfolio concurrently."""
    results = {}
    portfolio = state.get("portfolio", [])
    risk_tolerance = state.get("risk_tolerance", "moderate")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(_research_single_stock, h["ticker"], risk_tolerance) for h in portfolio]
        for future in concurrent.futures.as_completed(futures):
            try:
                t, result = future.result()
                results[t] = result
            except Exception as e:
                print(f"Error researching stock: {e}")
                
    return {"research_results": results}

def trend_node(state: PortfolioState) -> dict:
    """Aggregates technical trends and platform-wide social signals."""
    trends = {h["ticker"]: get_stock_price_info.invoke({"ticker": h["ticker"]}) for h in state.get("portfolio", [])}
    market = f"{get_trending_stocks.invoke({})}\n\n{get_platform_popular.invoke({})}"
    return {"trend_results": trends, "market_trends": market}

def synthesize_node(state: PortfolioState) -> dict:
    """Creates the final personalized Markdown report."""
    prompt = f"""
    Create a detailed Markdown report for {state['user_name']} ({state['risk_tolerance']} profile).
    Portfolio: {state['portfolio']}
    Research: {state['research_results']}
    Trends: {state['trend_results']}
    Market: {state['market_trends']}
    User Question: {state.get('chat_message', 'N/A')}
    """
    resp = llm.invoke([SystemMessage(content="You are a senior portfolio manager. Use professional Markdown."), HumanMessage(content=prompt)])
    return {"final_report": resp.content}
