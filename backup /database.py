import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "portfolio_db"

def get_user_profile(user_id: str):
    # Mock profile for personal portfolio
    return {
        "name": "Brinda",
        "risk_tolerance": "moderate",
        "portfolio": [
            {"ticker": "AAPL", "shares": 10, "buy_price": 150.0},
            {"ticker": "MSFT", "shares": 5, "buy_price": 300.0}
        ]
    }
