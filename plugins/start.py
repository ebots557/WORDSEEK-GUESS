import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from database import add_user, add_group

# Config se Owner ID uthayega
OWNER_ID = int(os.environ.get("OWNER_ID"))

START_TEXT = """
**ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴡᴏʀᴅsᴇᴇᴋ!**

ᴀ ғᴜɴ ᴀɴᴅ ᴄᴏᴍᴘᴇᴛɪᴛɪᴠᴇ ᴡᴏʀᴅʟᴇ-sᴛʏʟᴇ ɢᴀᴍᴇ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ ᴘʟᴀʏ ᴅɪʀᴇᴄᴛʟʏ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ.

**ǫᴜɪᴄᴋ sᴛᴀʀᴛ:**
• ᴜsᴇ /new ᴛᴏ sᴛᴀʀᴛ ᴀ ɴᴇᴡ ɢᴀᴍᴇ
• ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴀ ɢʀᴏᴜᴘ ᴡɪᴛʜ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ᴘʟᴀʏ ᴡɪᴛʜ ғʀɪᴇɴᴅs
• ᴜsᴇ /help ғᴏʀ ᴅᴇᴛᴀɪʟᴇᴅ ɪɴsᴛʀᴜᴄᴛɪᴏɴs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ

ʀᴇᴀᴅʏ ᴛᴏ ᴛᴇsᴛ ʏᴏᴜʀ ᴡᴏʀᴅ sᴋɪʟʟs? ʟᴇᴛ's ᴘʟᴀʏ!
"""

@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    # User ko DB mein add karein
    await add_user(message.from_user.id)
    
    # Notify Owner
    try:
        await client.send_message(OWNER_ID, f"🔔 **ɴᴇᴡ ᴜsᴇʀ ɴx**\n\n👤 {message.from_user.mention}\n🆔 `{message.from_user.id}`")
    except:
        pass # Agar owner ne bot start na kiya ho
    
    bot_info = await client.get_me()
    buttons = [
        [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ +", url=f"http://t.me/{bot_info.username}?startgroup=true")],
        [InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs ↗️", url="https://t.me/FexionBots"), InlineKeyboardButton("ʜᴇʟᴘ", callback_data="help_menu")],
        [InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ ↗️", url="https://t.me/WordguessnxChat")]
    ]
    await message.reply_text(START_TEXT, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.new_chat_members)
async def welcome_group(client, message):
    for member in message.new_chat_members:
        if member.id == (await client.get_me()).id:
            # Group ko DB mein add karein
            await add_group(message.chat.id)
            
            # Invite link generate karein
            try:
                inv_link = await client.export_chat_invite_link(message.chat.id)
            except:
                inv_link = "ɴᴏ ᴘᴇʀᴍɪssɪᴏɴ (ɴᴏ ʟɪɴᴋ)"
                
            # Notify Owner
            await client.send_message(OWNER_ID, f"🏰 **ɴᴇᴡ ɢʀᴏᴜᴘ ɴx**\n\n📛 {message.chat.title}\n🆔 `{message.chat.id}`\n🔗 {inv_link}")
            
            # Group mein welcome msg
            await message.reply_text("🎮 **ᴡᴏʀᴅsᴇᴇᴋ ɪs ʀᴇᴀᴅʏ!**\nᴜsᴇ /new ᴛᴏ sᴛᴀʀᴛ ᴀ ɢᴀᴍᴇ.")

# --- Ping Command Added ---
@Client.on_message(filters.command("ping"))
async def ping_cmd(client, message):
    start = time.time()
    msg = await message.reply_text("🚀 **ᴘɪɴɢɪɴɢ...**")
    end = time.time()
    ms = (end - start) * 1000
    await msg.edit_text(f"⚡ **ᴘᴏɴɢ!**\n`{int(ms)} ms`")
