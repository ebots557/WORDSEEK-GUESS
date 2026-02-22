import motor.motor_asyncio
import os
from datetime import datetime

# Environment se URL uthayega
MONGO_URL = os.environ.get("MONGO_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client["WordSeek"]

users = db["users"]
groups = db["groups"]
scores = db["scores"] # Schema: user_id, pts, type, createdAt

async def init_db():
    """Database Indexing taaki purana data khud delete ho jaye (RAM & Disk saving)"""
    # 1. Monthly data 30 din baad expire ho jayega
    await scores.create_index("createdAt", expireAfterSeconds=2592000) 
    # 2. Daily data (Optional) ke liye bhi indexing fast rakhta hai
    await scores.create_index([("user_id", 1), ("type", 1)])

async def add_user(user_id):
    """User ko database mein add/update karne ke liye"""
    await users.update_one({"_id": user_id}, {"$set": {"_id": user_id}}, upsert=True)

async def add_group(chat_id):
    """Group ko database mein add/update karne ke liye"""
    await groups.update_one({"_id": chat_id}, {"$set": {"_id": chat_id}}, upsert=True)

async def save_score(user_id, points):
    """Global, Monthly aur Yearly scores update karne ka logic"""
    now = datetime.now()
    
    # 1. All Time Score (Kabhi reset nahi hoga)
    await scores.update_one(
        {"user_id": user_id, "type": "all_time"},
        {"$inc": {"pts": points}, "$set": {"last_updated": now}},
        upsert=True
    )
    
    # 2. Monthly Score (Example: monthly_2_2026)
    # Isme 'createdAt' field TTL index ke wajah se 30 din baad ise delete kar degi
    month_key = f"monthly_{now.month}_{now.year}"
    await scores.update_one(
        {"user_id": user_id, "type": month_key},
        {"$inc": {"pts": points}, "$set": {"createdAt": now}}, 
        upsert=True
    )
    
    # 3. Yearly Score (Example: yearly_2026)
    year_key = f"yearly_{now.year}"
    await scores.update_one(
        {"user_id": user_id, "type": year_key},
        {"$inc": {"pts": points}, "$set": {"createdAt": now}},
        upsert=True
    )
    
    # 4. Daily Score (Taaki Today wala button chale)
    today_key = f"daily_{now.day}_{now.month}_{now.year}"
    await scores.update_one(
        {"user_id": user_id, "type": today_key},
        {"$inc": {"pts": points}, "$set": {"createdAt": now}},
        upsert=True
    )

async def get_stats():
    """Bot ke total stats nikalne ke liye"""
    u_count = await users.count_documents({})
    g_count = await groups.count_documents({})
    return u_count, g_count

# Authorized users collection handle karne ke liye (Admin.py ke liye)
authorized = db["authorized"]

async def is_user_auth(chat_id, user_id):
    """Check if user is authorized in a specific group"""
    res = await authorized.find_one({"chat_id": chat_id, "user_id": user_id})
    return True if res else False
