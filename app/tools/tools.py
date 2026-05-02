import yfinance as yf
from datetime import datetime, timezone
from langchain_core.tools import tool
from langchain_core.documents import Document
from app.database import vector_store, get_all_user_holdings

## --- Helper Functions ---
def _get_safe_now():
    """Returns timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)

## --- Tool Definitions ---

@tool
def fetch_stock_news(ticker: str) -> str:
    """Fetch latest 10 news articles for a ticker via yfinance."""
    try:
        stock = yf.Ticker(ticker.upper())
        news = stock.news
        if not news: 
            return f"No news found for {ticker}."
        
        articles = []
        for item in news[:10]:
            title = item.get("title", "No title")
            publisher = item.get("publisher", "Unknown")
            # Handle the timestamp conversion safely
            ts = item.get("providerPublishTime")
            time_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M") if ts else "N/A"
            link = item.get('link', '')
            articles.append(f"• [{publisher}] {title} ({time_str})\n  {link}")
        
        return f"📰 Latest News for {ticker.upper()}:\n\n" + "\n\n".join(articles)
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"

@tool
def get_stock_price_info(ticker: str) -> str:
    """Get price, 50-day Moving Average, and basic trend signal."""
    try:
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period="3mo")
        if hist.empty: 
            return f"No price data available for {ticker}."

        cp = hist["Close"].iloc[-1]
        ma50 = hist["Close"].rolling(window=50).mean().iloc[-1]
        
        # Trend logic with a 2% buffer for neutrality
        if cp > ma50 * 1.02:
            trend = "🟢 BULLISH"
        elif cp < ma50 * 0.98:
            trend = "🔴 BEARISH"
        else:
            trend = "🟡 NEUTRAL"
        
        return f"📊 {ticker.upper()} Analysis: Price ${cp:.2f}, 50-Day MA ${ma50:.2f}. Trend: {trend}"
    except Exception as e:
        return f"Error fetching price info: {str(e)}"

@tool
def search_market_cache(query: str, k: int = 5) -> str:
    """RAG tool: Search MongoDB Atlas for cached financial intelligence."""
    try:
        # Ensure your vector_store is correctly initialized in app.database
        results = vector_store.similarity_search(query, k=k)
        if not results: 
            return "No cached data found matching that query."
        
        output = []
        for i, doc in enumerate(results, 1):
            tref = doc.metadata.get('ticker', 'N/A')
            snippet = doc.page_content[:200].replace("\n", " ")
            output.append(f"{i}. [{tref}] {snippet}...")
            
        return "🔍 Cached Market Intelligence:\n\n" + "\n\n".join(output)
    except Exception as e:
        return f"Error searching vector cache: {str(e)}"

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
        return f"✅ Stored news for {ticker.upper()} in market cache."
    except Exception as e:
        return f"Error storing news: {str(e)}"

@tool
def get_trending_stocks() -> str:
    """Market Scanner: Get top movers from a preset watchlist."""
    watchlist = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA", "META", "AMZN"]
    movers = []
    
    for s in watchlist:
        try:
            # period="2d" is efficient for a quick delta
            h = yf.Ticker(s).history(period="2d")
            if len(h) < 2: continue
            
            prev_close = h["Close"].iloc[-2]
            curr_close = h["Close"].iloc[-1]
            change = ((curr_close - prev_close) / prev_close) * 100
            movers.append({"ticker": s, "price": curr_close, "change": change})
        except: 
            continue
    
    if not movers:
        return "Unable to fetch trending data at this time."

    # Sort by absolute change percentage
    movers.sort(key=lambda x: abs(x["change"]), reverse=True)
    
    lines = [f"🔥 Hot Stocks (Daily Change):"]
    for m in movers:
        emoji = "📈" if m['change'] > 0 else "📉"
        lines.append(f"  {emoji} {m['ticker']}: ${m['price']:.2f} ({m['change']:+.2f}%)")
        
    return "\n".join(lines)

@tool
def get_platform_popular() -> str:
    """Social Signal: Most held stocks across all users in MongoDB."""
    try:
        holdings = get_all_user_holdings() # Expecting a list of dicts: [{'_id': 'AAPL', 'holder_count': 50}]
        if not holdings: 
            return "No platform usage data available yet."
            
        lines = ["👥 Popular on Platform:"]
        for h in holdings[:5]:
            lines.append(f"  • {h.get('_id', 'Unknown')}: {h.get('holder_count', 0)} holders")
            
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching social signals: {str(e)}"

@tool
def get_ticker_details(ticker: str) -> str:
    """Deep Dive: Comprehensive financial stats and company summary."""
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        # Formatting large numbers for readability
        m_cap = info.get('marketCap', 0)
        formatted_cap = f"${m_cap/1e12:.2f}T" if m_cap > 1e12 else f"${m_cap/1e9:.2f}B"
        
        summary = info.get('longBusinessSummary', 'No summary available.')
        
        return (f"🏢 {ticker.upper()} Details:\n"
                f"  Sector: {info.get('sector', 'N/A')}\n"
                f"  Market Cap: {formatted_cap}\n"
                f"  P/E Ratio: {info.get('trailingPE', 'N/A')}\n"
                f"  Summary: {summary[:350]}...")
    except Exception as e:
        return f"Error fetching details for {ticker}: {str(e)}"