import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.environ["MONGO_URI"])
db = client["personal_portfolio"]

print(f"Deleted market_cache: {db.market_cache.delete_many({}).deleted_count}")
print(f"Deleted market_cache: {db.checkpoints.delete_many({}).deleted_count}")
print(f"Deleted market_cache: {db.checkpoint_writes.delete_many({}).deleted_count}")
print("Database cleared successfully.")
