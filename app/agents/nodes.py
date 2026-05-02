"""
app/agents/nodes.py — Agent Node Logic
=======================================
Implementation of Manager, Research, Trend, and Synthesis nodes.
"""

import os
import time
import logging
import concurrent.futures

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
    max_tokens=4000,
    max_retries=5,
    cohere_api_key=os.environ.get("COHERE_API_KEY"),
)

def manager_node(state: PortfolioState) -> dict:
    """Reads user profile and hydrates state."""
    logger.info(f"Manager Node: Fetching profile for user {state['user_id']}")
    profile = get_user_profile(state["user_id"])
    if not profile:
        logger.error(f"Manager Node: Profile for {state['user_id']} not found.")
        return {"final_report": "❌ User profile not found."}
    return {
        "user_name": profile.get("name", "Investor"),
        "risk_tolerance": profile.get("risk_tolerance", "moderate"),
        "portfolio": profile.get("portfolio", []),
    }

def _research_single_stock(t: str, risk_tolerance: str) -> tuple[str, str]:
    """Helper to process a single stock concurrently."""
    logger.info(f"Research Node: Starting research for {t}...")
    news = fetch_stock_news.invoke({"ticker": t})
    embed_and_store_news.invoke({"ticker": t, "news_text": news})
    intel = search_market_cache.invoke({"query": f"{t} outlook", "k": 2})
    details = get_ticker_details.invoke({"ticker": t})
    
    logger.info(f"Research Node: Analyzing {t} using LLM...")
    
    time.sleep(2) # Throttle to avoid rate limits
    prompt = f"Analyze {t} for a {risk_tolerance} investor.\nNews: {news}\nIntel: {intel}\nDetails: {details}"
    resp = llm.invoke([SystemMessage(content="You are a financial analyst."), HumanMessage(content=prompt)])
    return t, resp.content

def research_node(state: PortfolioState) -> dict:
    """Performs RAG-based research for each ticker in the portfolio concurrently."""
    results = {}
    portfolio = state.get("portfolio", [])
    risk_tolerance = state.get("risk_tolerance", "moderate")
    
    logger.info(f"Research Node: Processing portfolio of {len(portfolio)} stocks.")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(_research_single_stock, h["ticker"], risk_tolerance) for h in portfolio]
        for future in concurrent.futures.as_completed(futures):
            try:
                t, result = future.result()
                logger.info(f"Research Node: Completed research for {t}")
                results[t] = result
            except Exception as e:
                logger.error(f"Error researching stock: {e}")
                
    return {"research_results": results}

def trend_node(state: PortfolioState) -> dict:
    """Aggregates technical trends and platform-wide social signals."""
    logger.info("Trend Node: Gathering technical and market trends...")
    trends = {h["ticker"]: get_stock_price_info.invoke({"ticker": h["ticker"]}) for h in state.get("portfolio", [])}
    market = f"{get_trending_stocks.invoke({})}\n\n{get_platform_popular.invoke({})}"
    logger.info("Trend Node: Trend gathering complete.")
    return {"trend_results": trends, "market_trends": market}

def synthesize_node(state: PortfolioState) -> dict:
    """Creates the final personalized Markdown report."""
    logger.info("Synthesize Node: Generating final report...")
    prompt = f"""
    Create a detailed Markdown report for {state['user_name']} ({state['risk_tolerance']} profile).
    Portfolio: {state['portfolio']}
    Research: {state['research_results']}
    Trends: {state['trend_results']}
    Market: {state['market_trends']}
    User Question: {state.get('chat_message', 'N/A')}
    """
    resp = llm.invoke([SystemMessage(content="You are a senior portfolio manager. Use professional Markdown."), HumanMessage(content=prompt)])
    logger.info("Synthesize Node: Final report generated successfully.")
    return {"final_report": resp.content}
