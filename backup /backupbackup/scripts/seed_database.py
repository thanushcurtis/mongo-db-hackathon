"""
scripts/seed_database.py — Seed MongoDB with Mock Data
======================================================
Run: python scripts/seed_database.py
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.environ["MONGO_URI"])
db = client["personal_portfolio"]

def seed():
    users = [
        {
            "user_id": "hardcoded_user_1",
            "name": "Thanush Curtis",
            "risk_tolerance": "moderate",
            "portfolio": [
                {"ticker": "AAPL", "shares": 15, "buy_price": 178.50},
                {"ticker": "NVDA", "shares": 10, "buy_price": 450.00},
                {"ticker": "MSFT", "shares": 5, "buy_price": 380.00}
            ]
        }
    ]
    for u in users:
        db.user_profiles.update_one({"user_id": u["user_id"]}, {"$set": u}, upsert=True)
    print("✅ Database Seeded Successfully.")

if __name__ == "__main__":
    seed()
