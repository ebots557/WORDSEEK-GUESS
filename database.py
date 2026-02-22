import motor.motor_asyncio
import os
from datetime import datetime

MONGO_URL = os.environ.get("MONGO_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["WordSeek"]

users = db["users"]
groups = db["groups"]
scores = db["scores"] # Schema: user_id, pts, type (daily/monthly/yearly/all), timestamp

# Database Indexing for Auto-Delete (Optional but recommended)
# Monthly data 30 din baad khud delete ho jayega agar type "monthly" hai
async def init_db():
    await scores.create_index("createdAt", expireAfterSeconds=2592000) 

async def add_user(user_id):
    await users.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)

async def add_group(chat_id):
    await groups.update_one({"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True)

async def save_score(user_id, points):
    now = datetime.now()
    # 1. All Time Score
    await scores.update_one(
        {"user_id": user_id, "type": "all_time"},
        {"$inc": {"pts": points}, "$set": {"last_updated": now}},
        upsert=True
    )
    # 2. Monthly Score (Auto-reset logic via key)
    month_key = f"monthly_{now.month}_{now.year}"
    await scores.update_one(
        {"user_id": user_id, "type": month_key},
        {"$inc": {"pts": points}, "$set": {"createdAt": now}}, 
        upsert=True
    )
    # 3. Yearly Score
    year_key = f"yearly_{now.year}"
    await scores.update_one(
        {"user_id": user_id, "type": year_key},
        {"$inc": {"pts": points}, "$set": {"createdAt": now}},
        upsert=True
    )

async def get_stats():
    u_count = await users.count_documents({})
    g_count = await groups.count_documents({})
    return u_count, g_count
