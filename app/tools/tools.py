import time
import logging
import requests
import yfinance as yf
from datetime import datetime, timezone
from langchain_core.tools import tool
from langchain_core.documents import Document
from app.database import vector_store, get_all_user_holdings

logger = logging.getLogger(__name__)

## --- Helper Functions ---
# Setup a custom session to help avoid rate limits
yf_session = requests.Session()
yf_session.headers.update({"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})

def _get_safe_now():
    """Returns timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)

def _log_tool_result(tool_name: str, result: str) -> str:
    logger.info(f"[{tool_name}] Result: {result}")
    return result

## --- Tool Definitions ---

@tool
def fetch_stock_news(ticker: str) -> str:
    """Fetch latest 1 news article for a ticker via yfinance."""
    try:
        stock = yf.Ticker(ticker.upper(), session=yf_session)
        news = stock.news
        if not news: 
            return _log_tool_result("fetch_stock_news", f"No news found for {ticker}.")
        
        articles = []
        for item in news[:2]:
            content = item.get("content", {})
            title = content.get("title", "No title")
            publisher = content.get("provider", {}).get("displayName", "Unknown")
            time_str = content.get("pubDate", "N/A")
            link = content.get("canonicalUrl", {}).get("url", "")
            articles.append(f"• [{publisher}] {title} ({time_str})\n  {link}")
        
        res = f"📰 Latest News for {ticker.upper()}:\n\n" + "\n\n".join(articles)
        return _log_tool_result("fetch_stock_news", res)
    except Exception as e:
        return _log_tool_result("fetch_stock_news", f"Error fetching news for {ticker}: {str(e)}")

@tool
def get_stock_price_info(ticker: str) -> str:
    """Get price, 50-day Moving Average, and basic trend signal."""
    try:
        stock = yf.Ticker(ticker.upper(), session=yf_session)
        hist = stock.history(period="3mo")
        if hist.empty: 
            return _log_tool_result("get_stock_price_info", f"No price data available for {ticker}.")

        cp = hist["Close"].iloc[-1]
        ma50 = hist["Close"].rolling(window=50).mean().iloc[-1]
        
        # Trend logic with a 2% buffer for neutrality
        if cp > ma50 * 1.02:
            trend = "🟢 BULLISH"
        elif cp < ma50 * 0.98:
            trend = "🔴 BEARISH"
        else:
            trend = "🟡 NEUTRAL"
        
        res = f"📊 {ticker.upper()} Analysis: Price ${cp:.2f}, 50-Day MA ${ma50:.2f}. Trend: {trend}"
        return _log_tool_result("get_stock_price_info", res)
    except Exception as e:
        return _log_tool_result("get_stock_price_info", f"Error fetching price info: {str(e)}")

@tool
def search_market_cache(query: str, k: int = 5) -> str:
    """RAG tool: Search MongoDB Atlas for cached financial intelligence."""
    try:
        # Ensure your vector_store is correctly initialized in app.database
        results = vector_store.similarity_search(query, k=k)
        if not results: 
            return _log_tool_result("search_market_cache", "No cached data found matching that query.")
        
        output = []
        for i, doc in enumerate(results, 1):
            tref = doc.metadata.get('ticker', 'N/A')
            snippet = doc.page_content[:200].replace("\n", " ")
            output.append(f"{i}. [{tref}] {snippet}...")
            
        res = "🔍 Cached Market Intelligence:\n\n" + "\n\n".join(output)
        return _log_tool_result("search_market_cache", res)
    except Exception as e:
        return _log_tool_result("search_market_cache", f"Error searching vector cache: {str(e)}")

@tool
def embed_and_store_news(ticker: str, news_text: str) -> str:
    """Store news in MongoDB market_cache collection with Voyage embeddings."""
    try:
        doc = Document(
            page_content=news_text,
            metadata={
                "ticker": ticker.upper(), 
                "source": "yfinance", 
                "timestamp": _get_safe_now().isoformat()
            }
        )
        vector_store.add_documents([doc])
        return _log_tool_result("embed_and_store_news", f"✅ Stored news for {ticker.upper()} in market cache.")
    except Exception as e:
        return _log_tool_result("embed_and_store_news", f"Error storing news: {str(e)}")

import urllib.request
import json

def get_trending_stocks_data():
    """Helper function to fetch structured trending data dynamically."""
    watchlist = []
    try:
        req = urllib.request.Request(
            'https://query1.finance.yahoo.com/v1/finance/trending/US?count=10', 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        res = urllib.request.urlopen(req).read()
        data = json.loads(res)
        quotes = data.get('finance', {}).get('result', [{}])[0].get('quotes', [])
        # Filter out cryptos and indices if preferred, or keep them. Here we just take up to 10 symbols.
        watchlist = [q['symbol'] for q in quotes if '^' not in q['symbol']][:8]
    except Exception as e:
        print(f"Failed to fetch trending symbols: {e}")
        watchlist = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "AMZN"] # Fallback

    movers = []
    
    for s in watchlist:
        try:
            time.sleep(2) # Throttle to prevent rate limit
            # period="2d" is efficient for a quick delta
            stock = yf.Ticker(s, session=yf_session)
            h = stock.history(period="2d")
            if len(h) < 2: continue
            
            prev_close = h["Close"].iloc[-2]
            curr_close = h["Close"].iloc[-1]
            change = ((curr_close - prev_close) / prev_close) * 100
            movers.append({"ticker": s, "price": curr_close, "change": change})
        except: 
            continue
            
    movers.sort(key=lambda x: abs(x["change"]), reverse=True)
    return movers

@tool
def get_trending_stocks() -> str:
    """Market Scanner: Get top movers from a preset watchlist."""
    movers = get_trending_stocks_data()
    
    if not movers:
        return _log_tool_result("get_trending_stocks", "Unable to fetch trending data at this time.")

    # Sort by absolute change percentage
    movers.sort(key=lambda x: abs(x["change"]), reverse=True)
    
    lines = [f"🔥 Hot Stocks (Daily Change):"]
    for m in movers:
        emoji = "📈" if m['change'] > 0 else "📉"
        lines.append(f"  {emoji} {m['ticker']}: ${m['price']:.2f} ({m['change']:+.2f}%)")
        
    return _log_tool_result("get_trending_stocks", "\n".join(lines))

@tool
def get_platform_popular() -> str:
    """Social Signal: Most held stocks across all users in MongoDB."""
    try:
        holdings = get_all_user_holdings() # Expecting a list of dicts: [{'_id': 'AAPL', 'holder_count': 50}]
        if not holdings: 
            return _log_tool_result("get_platform_popular", "No platform usage data available yet.")
            
        lines = ["👥 Popular on Platform:"]
        for h in holdings[:5]:
            lines.append(f"  • {h.get('_id', 'Unknown')}: {h.get('holder_count', 0)} holders")
            
        return _log_tool_result("get_platform_popular", "\n".join(lines))
    except Exception as e:
        return _log_tool_result("get_platform_popular", f"Error fetching social signals: {str(e)}")

@tool
def get_ticker_details(ticker: str) -> str:
    """Deep Dive: Comprehensive financial stats and company summary."""
    try:
        stock = yf.Ticker(ticker.upper(), session=yf_session)
        info = stock.info
        
        # Formatting large numbers for readability
        m_cap = info.get('marketCap', 0)
        formatted_cap = f"${m_cap/1e12:.2f}T" if m_cap > 1e12 else f"${m_cap/1e9:.2f}B"
        
        summary = info.get('longBusinessSummary', 'No summary available.')
        
        res = (f"🏢 {ticker.upper()} Details:\n"
                f"  Sector: {info.get('sector', 'N/A')}\n"
                f"  Market Cap: {formatted_cap}\n"
                f"  P/E Ratio: {info.get('trailingPE', 'N/A')}\n"
                f"  Summary: {summary[:350]}...")
        return _log_tool_result("get_ticker_details", res)
    except Exception as e:
        return _log_tool_result("get_ticker_details", f"Error fetching details for {ticker}: {str(e)}")