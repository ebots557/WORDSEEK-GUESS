import asyncio
from pyrogram import Client, filters
from database import get_stats, users, groups
import os
import time

OWNER_ID = int(os.environ.get("OWNER_ID"))
start_time = time.time()

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
    # Broadcast to Users
    async for user in all_users:
        try:
            await msg.forward(user["_id"])
            done += 1
            await asyncio.sleep(0.3) # Anti-ban delay
        except: pass
    
    # Broadcast to Groups
    async for group in all_groups:
        try:
            await msg.forward(group["_id"])
            done += 1
            await asyncio.sleep(0.5) # Group delay is higher
        except: pass
        
    await message.reply_text(f"✅ **ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ ɴx**\nSent to {done} chats.")
