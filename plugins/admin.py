import asyncio
import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from database import get_stats, users, groups, db # db for custom collections

# Collections for Auth and Topics
auth_db = db["authorized_users"]
topic_db = db["game_topics"]

OWNER_ID = int(os.environ.get("OWNER_ID"))
start_time = time.time()

# --- Utility Functions ---

async def is_admin(chat_id, user_id, client):
    """Check if user is admin or owner"""
    if user_id == OWNER_ID:
        return True
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except:
        return False

# --- Admin Commands ---

@Client.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    u, g = await get_stats()
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - start_time))
    await message.reply_text(f"📊 **ʙᴏᴛ sᴛᴀᴛs ɴx**\n\n👥 ᴜsᴇʀs: {u}\n🏰 ɢʀᴏᴜᴘs: {g}\n⏳ ᴜᴘᴛɪᴍᴇ: {uptime}")

@Client.on_message(filters.command("gcast") & filters.user(OWNER_ID))
async def broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ɴx")
    
    msg = message.reply_to_message
    all_users = users.find({})
    all_groups = groups.find({})
    
    done = 0
    await message.reply_text("🚀 **ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛᴇᴅ ɴx...**")
    
    async for user in all_users:
        try:
            await msg.forward(user["_id"])
            done += 1
            await asyncio.sleep(0.3)
        except: pass
    
    async for group in all_groups:
        try:
            await msg.forward(group["_id"])
            done += 1
            await asyncio.sleep(1.5)
        except: pass
        
    await message.reply_text(f"✅ **ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ ɴx**\nsᴇɴᴛ ᴛᴏ {done} ᴄʜᴀᴛs.")

# --- SeekAuth Logic (Screenshot 2) ---

@Client.on_message(filters.command("seekauth") & filters.group)
async def seekauth_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id, client):
        return await message.reply_text("❌ **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɴx**")

    args = message.text.split()
    chat_id = message.chat.id

    # /seekauth list
    if len(args) > 1 and args[1].lower() == "list":
        auths = await auth_db.find_one({"_id": chat_id})
        if not auths or not auths.get("users"):
            return await message.reply_text("ɴᴏ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ғᴏᴜɴᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ ɴx.")
        
        user_list = ""
        for u_id in auths["users"]:
            try:
                u = await client.get_users(u_id)
                user_list += f"• {u.mention} (`{u_id}`)\n"
            except:
                user_list += f"• Unknown (`{u_id}`)\n"
        return await message.reply_text(f"📝 **ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ɴx:**\n\n{user_list}")

    # Identify User (Reply or Mention)
    user_id = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(args) > 1:
        # Handle remove logic
        if args[1].lower() == "remove":
            if len(args) < 3 and not message.reply_to_message:
                return await message.reply_text("ᴘʟᴇᴀsᴇ ᴍᴇɴᴛɪᴏɴ ᴀ ᴜsᴇʀ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ʀᴇᴍᴏᴠᴇ.")
            target = args[2] if len(args) > 2 else message.reply_to_message.from_user.id
            try:
                u = await client.get_users(target)
                user_id = u.id
                await auth_db.update_one({"_id": chat_id}, {"$pull": {"users": user_id}})
                return await message.reply_text(f"✅ {u.mention} **ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ɴx.**")
            except:
                return await message.reply_text("❌ **ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɴx.**")
        else:
            try:
                u = await client.get_users(args[1])
                user_id = u.id
            except:
                return await message.reply_text("❌ **ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɴx.**")

    if user_id:
        await auth_db.update_one({"_id": chat_id}, {"$addToSet": {"users": user_id}}, upsert=True)
        u = await client.get_users(user_id)
        await message.reply_text(f"✅ {u.mention} **ɪs ɴᴏᴡ ᴀɴ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀ ɴx.**")
    else:
        await message.reply_text("💡 **ᴜsᴀɢᴇ:**\n`/seekauth @username` - ᴀᴅᴅ\n`/seekauth remove @username` - ʀᴇᴍᴏᴠᴇ\n`/seekauth list` - sʜᴏᴡ ᴀʟʟ")

@Client.on_message(filters.command("rmallauth") & filters.group)
async def remove_all_auth(client, message):
    if not await is_admin(message.chat.id, message.from_user.id, client):
        return await message.reply_text("❌ **ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɴx**")
    
    await auth_db.delete_one({"_id": message.chat.id})
    await message.reply_text("🗑️ **ᴀʟʟ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴛʜɪs ɢʀᴏᴜᴘ ɴx.**")

# --- Game Topic Logic (Screenshot 2) ---

@Client.on_message(filters.command("setgametopic") & filters.group)
async def set_topic(client, message):
    if not await is_admin(message.chat.id, message.from_user.id, client):
        return
    
    topic_id = message.reply_to_message.reply_to_message_id if message.reply_to_message else message.message_thread_id
    if not topic_id:
        return await message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴsɪᴅᴇ ᴀ ғᴏʀᴜᴍ ᴛᴏᴘɪᴄ ɴx.")
    
    await topic_db.update_one({"_id": message.chat.id}, {"$addToSet": {"topics": topic_id}}, upsert=True)
    await message.reply_text("✅ **ᴛʜɪs ᴛᴏᴘɪᴄ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴀs ᴀ ɢᴀᴍᴇ ᴛᴏᴘɪᴄ ɴx.**")

@Client.on_message(filters.command("unsetgametopic") & filters.group)
async def unset_topic(client, message):
    if not await is_admin(message.chat.id, message.from_user.id, client):
        return
    
    await topic_db.delete_one({"_id": message.chat.id})
    await message.reply_text("✅ **ᴛᴏᴘɪᴄ ʀᴇsᴛʀɪᴄᴛɪᴏɴs ʀᴇᴍᴏᴠᴇᴅ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ ɴx.**")
