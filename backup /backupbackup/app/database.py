"""
app/database.py — MongoDB Connection & Voyage Embeddings
========================================================
Centralized database and embedding model initialization.
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_voyageai import VoyageAIEmbeddings
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch

# ── Environment Setup ───────────────────────────────────────────────
load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")
VOYAGE_API_KEY = os.environ.get("VOYAGE_API_KEY")

if not MONGO_URI or not VOYAGE_API_KEY:
    raise ValueError("Missing MONGO_URI or VOYAGE_API_KEY in environment variables.")

# ── Database Config ──────────────────────────────────────────────────
DB_NAME = "personal_portfolio"
USER_PROFILES_COLLECTION = "user_profiles"
MARKET_CACHE_COLLECTION = "market_cache"

# ── MongoDB Client (Singleton) ──────────────────────────────────────
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collection handles
user_profiles = db[USER_PROFILES_COLLECTION]
market_cache_collection = db[MARKET_CACHE_COLLECTION]

# ── Voyage AI Embeddings (voyage-finance-2) ─────────────────────────
# Specialized for financial data, 1024 dimensions.
embeddings = VoyageAIEmbeddings(
    voyage_api_key=VOYAGE_API_KEY,
    model="voyage-finance-2",
)

# ── MongoDB Atlas Vector Store ──────────────────────────────────────
# Wraps market_cache for RAG similarity search.
vector_store = MongoDBAtlasVectorSearch(
    collection=market_cache_collection,
    embedding=embeddings,
    index_name="vector_index",
    text_key="content",
    embedding_key="embedding",
)

# ── Database Helpers ────────────────────────────────────────────────
def get_user_profile(user_id: str) -> dict | None:
    """Fetch user risk profile and portfolio from MongoDB."""
    return user_profiles.find_one({"user_id": user_id}, {"_id": 0})

def get_all_user_holdings() -> list[dict]:
    """Aggregates all user holdings for platform trend analysis."""
    pipeline = [
        {"$unwind": "$portfolio"},
        {
            "$group": {
                "_id": "$portfolio.ticker",
                "total_shares": {"$sum": "$portfolio.shares"},
                "holder_count": {"$sum": 1},
            }
        },
        {"$sort": {"holder_count": -1}},
    ]
    return list(user_profiles.aggregate(pipeline))
