from pymongo import MongoClient
from datetime import datetime, UTC
from dotenv import load_dotenv
import os

# ✅ Load .env file
load_dotenv()

# ✅ Get URI from environment
mongo_uri = os.getenv("MONGO_URI")

# ✅ Use the variable, not a hardcoded string
client = MongoClient(mongo_uri)
db = client["webhook_db"]
collection = db["events"]

collection.insert_one({
  "author": "Test User",
  "action": "push",
  "from_branch": "",
  "to_branch": "main",
  "timestamp": datetime.now(UTC)
})

print("Inserted!")
