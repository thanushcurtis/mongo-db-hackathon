"""
agents.py — LangGraph Multi-Agent Orchestration
=================================================
Defines the StateGraph with three agent nodes:

  1. Manager Agent  — reads user profile, dispatches research & trend tasks,
                      synthesizes the final Markdown report.
  2. Research Agent — uses RAG pipeline (yfinance + Voyage AI + MongoDB Vector
                      Search) to analyze sentiment and produce buy/sell/hold
                      recommendations per ticker.
  3. Trend Agent   — uses yfinance for price/MA trend signals and finds hot
                      stocks across the market and the platform.

State flows:
  manager_node → research_node (parallel per ticker) → trend_node → manager_synthesize
"""

from click import clear
import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv

from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.mongodb import MongoDBSaver

from backup .database import get_user_profile, MONGO_URI, DB_NAME
from tools import (
    fetch_stock_news,
    get_stock_price_info,
    search_market_cache,
    embed_and_store_news,
    get_trending_stocks,
    get_platform_popular,
    get_ticker_details,
)

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────
llm = ChatCohere(
    model="command-a-03-2025",
    temperature=0.3,
    cohere_api_key=os.environ["COHERE_API_KEY"],
)


# ─────────────────────────────────────────────────────────────────────
# STATE DEFINITION
# ─────────────────────────────────────────────────────────────────────
class PortfolioState(TypedDict):
    """
    The shared state passed between all nodes in the graph.
    """
    # Input
    user_id: str
    chat_message: str            # optional chat message from user

    # User profile (populated by manager)
    user_name: str
    risk_tolerance: str          # "conservative", "moderate", "aggressive"
    portfolio: list[dict]        # [{ticker, shares, buy_price}, ...]

    # Research results (populated by research_node)
    research_results: dict       # {ticker: analysis_string, ...}

    # Trend results (populated by trend_node)
    trend_results: dict          # {ticker: trend_string, ...}
    market_trends: str           # hot stocks & platform popularity

    # Final output
    final_report: str            # synthesized Markdown report


# ─────────────────────────────────────────────────────────────────────
# NODE 1: MANAGER — Read profile & prepare tasks
# ─────────────────────────────────────────────────────────────────────
def manager_node(state: PortfolioState) -> dict:
    """
    Reads the user profile from MongoDB and populates state with
    user info, risk tolerance, and portfolio holdings.
    """
    user_id = state["user_id"]
    profile = get_user_profile(user_id)

    if not profile:
        return {
            "user_name": "Unknown User",
            "risk_tolerance": "moderate",
            "portfolio": [],
            "final_report": f"❌ No profile found for user_id: {user_id}",
        }

    return {
        "user_name": profile.get("name", "User"),
        "risk_tolerance": profile.get("risk_tolerance", "moderate"),
        "portfolio": profile.get("portfolio", []),
    }


# ─────────────────────────────────────────────────────────────────────
# NODE 2: RESEARCH — Analyze each ticker with RAG pipeline
# ─────────────────────────────────────────────────────────────────────
def research_node(state: PortfolioState) -> dict:
    """
    For each ticker in the user's portfolio:
      1. Fetch latest news via yfinance
      2. Embed and store news in MongoDB vector cache
      3. Search the vector cache for relevant intelligence
      4. Get detailed ticker info (financials, analyst ratings)
      5. Use Cohere LLM to produce a sentiment analysis + recommendation
    """
    portfolio = state.get("portfolio", [])
    risk_tolerance = state.get("risk_tolerance", "moderate")

    if not portfolio:
        return {"research_results": {}}

    research_results = {}

    for holding in portfolio:
        ticker = holding["ticker"]
        shares = holding.get("shares", 0)
        buy_price = holding.get("buy_price", 0)

        # Step 1: Fetch fresh news
        news_text = fetch_stock_news.invoke({"ticker": ticker})

        # Step 2: Embed and store in market cache for RAG
        embed_and_store_news.invoke({"ticker": ticker, "news_text": news_text})

        # Step 3: Search cached intelligence
        cached_intel = search_market_cache.invoke(
            {"query": f"{ticker} financial analysis sentiment", "k": 3}
        )

        # Step 4: Get detailed ticker information
        details = get_ticker_details.invoke({"ticker": ticker})

        # Step 5: LLM analysis with all context
        analysis_prompt = f"""You are a senior financial analyst. Analyze this stock for an investor with {risk_tolerance} risk tolerance.

**Ticker:** {ticker}
**Holdings:** {shares} shares bought at ${buy_price:.2f} each

**Latest News:**
{news_text}

**Cached Market Intelligence:**
{cached_intel}

**Company Details:**
{details}

Provide a concise analysis covering:
1. **Current Sentiment** (Bullish/Bearish/Neutral) with reasoning
2. **Key Risks** specific to this stock right now
3. **Recommendation** (BUY MORE / HOLD / SELL / REDUCE POSITION) with clear rationale
4. **Price Outlook** — where the stock might go in the next 1-3 months
5. **Action Items** — specific steps for the investor

Be direct and actionable. Consider the investor's {risk_tolerance} risk tolerance when making recommendations.
"""

        response = llm.invoke(
            [
                SystemMessage(content="You are a financial research analyst producing actionable investment reports."),
                HumanMessage(content=analysis_prompt),
            ]
        )

        research_results[ticker] = response.content

    return {"research_results": research_results}


# ─────────────────────────────────────────────────────────────────────
# NODE 3: TREND — Market trends + platform signals
# ─────────────────────────────────────────────────────────────────────
def trend_node(state: PortfolioState) -> dict:
    """
    Performs two analyses:
      1. For each ticker in portfolio — get price/MA trend signal
      2. Get market-wide hot stocks + platform popularity
    """
    portfolio = state.get("portfolio", [])

    # Per-ticker trends
    trend_results = {}
    for holding in portfolio:
        ticker = holding["ticker"]
        trend_data = get_stock_price_info.invoke({"ticker": ticker})
        trend_results[ticker] = trend_data

    # Market-wide trends
    hot_stocks = get_trending_stocks.invoke({})
    platform_pop = get_platform_popular.invoke({})
    market_trends = f"{hot_stocks}\n\n{platform_pop}"

    return {
        "trend_results": trend_results,
        "market_trends": market_trends,
    }


# ─────────────────────────────────────────────────────────────────────
# NODE 4: SYNTHESIZE — Final Markdown report
# ─────────────────────────────────────────────────────────────────────
def synthesize_node(state: PortfolioState) -> dict:
    """
    Takes all research and trend data and produces a comprehensive
    Markdown report tailored to the user's risk profile.
    """
    user_name = state.get("user_name", "Investor")
    risk_tolerance = state.get("risk_tolerance", "moderate")
    portfolio = state.get("portfolio", [])
    research_results = state.get("research_results", {})
    trend_results = state.get("trend_results", {})
    market_trends = state.get("market_trends", "")
    chat_message = state.get("chat_message", "")

    # Build context for final synthesis
    portfolio_summary = ""
    for h in portfolio:
        ticker = h["ticker"]
        portfolio_summary += (
            f"- **{ticker}**: {h.get('shares', 0)} shares "
            f"@ ${h.get('buy_price', 0):.2f}\n"
        )

    research_section = ""
    for ticker, analysis in research_results.items():
        research_section += f"\n### {ticker}\n{analysis}\n"

    trend_section = ""
    for ticker, trend in trend_results.items():
        trend_section += f"\n### {ticker}\n{trend}\n"

    # Determine if this was triggered by a chat question
    chat_context = ""
    if chat_message:
        chat_context = f"\nThe user specifically asked: \"{chat_message}\"\nMake sure to directly answer their question in the report.\n"

    synthesis_prompt = f"""You are a senior portfolio manager preparing a personalized investment report.

**Client:** {user_name}
**Risk Profile:** {risk_tolerance}
{chat_context}

**Current Portfolio:**
{portfolio_summary}

**Individual Stock Research:**
{research_section}

**Technical Trend Analysis:**
{trend_section}

**Market Overview:**
{market_trends}

Generate a comprehensive, beautifully formatted Markdown report with the following sections:

# 📊 Portfolio Analysis Report for {user_name}

## Executive Summary
Brief overview of the portfolio's health, key findings, and top priority actions.

## 📈 Individual Stock Analysis
For each stock, include:
- Current position value vs. purchase value (P&L)
- Sentiment and recommendation (BUY/HOLD/SELL)
- Key risks and catalysts

## 📉 Technical Trends
Trend signals, moving average analysis, and momentum indicators.

## 🔥 Market Opportunities
Hot stocks and trending picks that align with the user's {risk_tolerance} risk profile.

## 👥 Platform Insights
What other investors on our platform are holding and trading.

## ✅ Action Plan
Numbered list of specific, prioritized actions the investor should take NOW.

Important: Tailor ALL recommendations to the **{risk_tolerance}** risk tolerance:
- Conservative: Focus on stability, dividends, blue-chips. Avoid volatile picks.
- Moderate: Balance growth and safety. Suggest diversification.
- Aggressive: Highlight high-growth, momentum plays. Accept volatility.

Use emojis, tables, and clear formatting to make the report engaging and easy to scan.
"""

    response = llm.invoke(
        [
            SystemMessage(content="You are a portfolio manager who creates visually stunning, actionable investment reports in Markdown."),
            HumanMessage(content=synthesis_prompt),
        ]
    )

    return {"final_report": response.content}


# ─────────────────────────────────────────────────────────────────────
# ROUTING LOGIC — Skip to end if no portfolio found
# ─────────────────────────────────────────────────────────────────────
def should_continue(state: PortfolioState) -> str:
    """
    After manager_node: if portfolio is empty (bad user_id), skip to end.
    Otherwise continue to research.
    """
    if not state.get("portfolio"):
        return "end"
    return "research"


# ─────────────────────────────────────────────────────────────────────
# BUILD THE GRAPH
# ─────────────────────────────────────────────────────────────────────
def build_graph():
    """
    Constructs and compiles the LangGraph StateGraph with MongoDB
    checkpointing.

    Graph flow:
      manager → (if portfolio) → research → trend → synthesize → END
      manager → (if no portfolio) → END
    """
    # Create the state graph
    builder = StateGraph(PortfolioState)

    # Add nodes
    builder.add_node("manager", manager_node)
    builder.add_node("research", research_node)
    builder.add_node("trend", trend_node)
    builder.add_node("synthesize", synthesize_node)

    # Set entry point
    builder.set_entry_point("manager")

    # Conditional edge from manager: continue or stop
    builder.add_conditional_edges(
        "manager",
        should_continue,
        {
            "research": "research",
            "end": END,
        },
    )

    # Linear flow: research → trend → synthesize → END
    builder.add_edge("research", "trend")
    builder.add_edge("trend", "synthesize")
    builder.add_edge("synthesize", END)

    # Compile with MongoDB checkpointer
    # Note: MongoDBSaver.from_conn_string() returns a context manager,
    # so for module-level usage we instantiate directly with a MongoClient.
    from pymongo import MongoClient as _MongoClient

    _checkpoint_client = _MongoClient(MONGO_URI)
    checkpointer = MongoDBSaver(
        client=_checkpoint_client,
        db_name=DB_NAME,
    )
    graph = builder.compile(checkpointer=checkpointer)

    return graph


# ── Compiled graph (module-level singleton) ──────────────────────────
graph = build_graph()
clear