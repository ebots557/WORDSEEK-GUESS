import motor.motor_asyncio
import os
from datetime import datetime

MONGO_URL = os.environ.get("MONGO_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["WordSeek"]

users = db["users"]
groups = db["groups"]
scores = db["scores"] 
authorized = db["authorized"]

async def init_db():
    # TTL Index: Automatically delete documents after 30 days to save space
    await scores.create_index("createdAt", expireAfterSeconds=2592000) 
    # Index for faster queries on user and type
    await scores.create_index([("user_id", 1), ("type", 1), ("chat_id", 1)])

async def add_user(user_id):
    await users.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)

async def add_group(chat_id):
    await groups.update_one({"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True)

async def save_score(user_id, chat_id, points):
    now = datetime.now()
    
    # List of period types to update
    # Global records use chat_id="global", Group records use actual chat_id
    periods = [
        "all_time",
        f"daily_{now.day}_{now.month}_{now.year}",
        f"weekly_{now.isocalendar()[1]}_{now.year}",
        f"monthly_{now.month}_{now.year}",
        f"yearly_{now.year}"
    ]
    
    for p_key in periods:
        # Update Global Stats
        await scores.update_one(
            {"user_id": user_id, "type": p_key, "chat_id": "global"},
            {"$inc": {"pts": points}, "$set": {"createdAt": now}},
            upsert=True
        )
        # Update Group Specific Stats (This Chat)
        if chat_id != "private":
            await scores.update_one(
                {"user_id": user_id, "type": p_key, "chat_id": chat_id},
                {"$inc": {"pts": points}, "$set": {"createdAt": now}},
                upsert=True
            )

async def get_stats():
    u_count = await users.count_documents({})
    g_count = await groups.count_documents({})
    return u_count, g_count

async def is_user_auth(chat_id, user_id):
    res = await authorized.find_one({"chat_id": chat_id, "user_id": user_id})
    return True if res else False
