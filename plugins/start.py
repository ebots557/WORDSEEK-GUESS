from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from database import add_user, add_group

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

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    await add_user(message.from_user.id)
    # Notify Owner
    await client.send_message(OWNER_ID, f"🔔 **ɴᴇᴡ ᴜsᴇʀ ɴx**\n\n👤 {message.from_user.mention}\n🆔 `{message.from_user.id}`")
    
    buttons = [
        [InlineKeyboardButton("ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ +", url=f"http://t.me/yourbot?startgroup=true")],
        [InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs ↗️", url="https://t.me/yourchannel"), InlineKeyboardButton("ʜᴇʟᴘ", callback_data="help_menu")],
        [InlineKeyboardButton("ᴅɪsᴄᴜssɪᴏɴ ↗️", url="https://t.me/yourgroup")]
    ]
    await message.reply_text(START_TEXT, reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_message(filters.new_chat_members)
async def welcome_group(client, message):
    for member in message.new_chat_members:
        if member.id == (await client.get_me()).id:
            await add_group(message.chat.id)
            inv_link = await message.chat.export_invite_link() if message.chat.username else "No Link"
            await client.send_message(OWNER_ID, f"🏰 **ɴᴇᴡ ɢʀᴏᴜᴘ ɴx**\n\n📛 {message.chat.title}\n🆔 `{message.chat.id}`\n🔗 {inv_link}")
