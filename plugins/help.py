import os
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import scores # Database se scores fetch karne ke liye

# Owner ID environmental variables se uthayega
OWNER_ID = int(os.environ.get("OWNER_ID", "7589623332"))

@Client.on_message(filters.command("help"))
async def help_cmd(client, message):
    text = """
▶ **ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs (ᴀᴅᴍɪɴ ᴏɴʟʏ)**

**ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs**
/seekauth – ᴍᴀɴᴀɢᴇ ᴜsᴇʀs ᴡʜᴏ ᴄᴀɴ ᴇɴᴅ ɢᴀᴍᴇs ᴡɪᴛʜᴏᴜᴛ ᴀ ᴠᴏᴛᴇ.

**ᴜsᴀɢᴇ:**
• `/seekauth @username` – ᴀᴜᴛʜᴏʀɪᴢᴇ ᴀ ᴜsᴇʀ
• `/seekauth remove @username` – ʀᴇᴍᴏᴠᴇ ᴀᴜᴛʜᴏʀɪᴢᴀᴛɪᴏɴ
• `/seekauth list` – ʟɪsᴛ ᴀʟʟ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs
• `/rmallauth` – ʀᴇᴍᴏᴠᴇ ᴀʟʟ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs (ɢʀᴏᴜᴘ cleanup)

ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴜsᴇ ᴀ ᴜsᴇʀ ɪᴅ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ɪɴsᴛᴇᴀᴅ ᴏғ `@username`.

**ɢᴀᴍᴇ ᴛᴏᴘɪᴄ (ғᴏʀᴜᴍ ɢʀᴏᴜᴘs)**
/setgametopic – ʀᴇsᴛʀɪᴄᴛ ɢᴀᴍᴇs ᴛᴏ ᴏɴᴇ ᴏʀ ᴍᴏʀᴇ ᴛᴏᴘɪᴄs
ʀᴜɴ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ _ɪɴsɪᴅᴇ ᴛʜᴇ ᴛᴏᴘɪᴄ_ ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ɢᴀᴍᴇs ᴛᴏ ʙᴇ ᴘʟᴀʏᴇᴅ.
ᴀғᴛᴇʀ sᴇᴛᴛɪɴɢ, ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ᴏɴʟʏ ʀᴜɴ ɢᴀᴍᴇs ɪɴ ᴛʜᴀᴛ ᴛᴏᴘɪᴄ.

/unsetgametopic – ʀᴇᴍᴏᴠᴇ ᴛᴏᴘɪᴄ ʀᴇsᴛʀɪᴄᴛɪᴏɴ
**ᴜsᴀɢᴇ:** `/unsetgametopic`
ᴀғᴛᴇʀ ᴜɴsᴇᴛᴛɪɴɢ, ᴛʜᴇ ʙᴏᴛ ᴄᴀɴ ʀᴜɴ ɢᴀᴍᴇs ɪɴ ᴀɴʏ ᴛᴏᴘɪᴄ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ ᴀɢᴀɪɴ.
"""
    buttons = [
        [
            InlineKeyboardButton("ʜᴏᴡ ᴛᴏ ᴘʟᴀʏ", callback_data="how_to_play"), 
            InlineKeyboardButton("ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ & sᴄᴏʀᴇs", callback_data="lb_scores")
        ],
        [
            InlineKeyboardButton("ᴏᴡɴᴇʀ", url="tg://user?id=7589623332")
        ]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("how_to_play"))
async def how_to_play(client, cb):
    text = """
▶ **ʜᴏᴡ ᴛᴏ ᴘʟᴀʏ ᴡᴏʀᴅsᴇᴇᴋ**

1. sᴛᴀʀᴛ ᴀ ɢᴀᴍᴇ ᴜsɪɴɢ /new ᴄᴏᴍᴍᴀɴᴅ
2. ɢᴜᴇss ᴀ ʀᴀɴᴅᴏᴍ 5-ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ
3. ᴀғᴛᴇʀ ᴇᴀᴄʜ ɢᴜᴇss, ʏᴏᴜ'ʟʟ ɢᴇᴛ ᴄᴏʟᴏʀ ʜɪɴᴛs:
   🟩 ᴄᴏʀʀᴇᴄᴛ ʟᴇᴛᴛᴇʀ ɪɴ ᴛʜᴇ ʀɪɢʜᴛ sᴘᴏᴛ
   🟨 ᴄᴏʀʀᴇᴄᴛ ʟᴇᴛᴛᴇʀ ɪɴ ᴛʜᴇ ᴡʀᴏɴɢ sᴘᴏᴛ
   🟥 ʟᴇᴛᴛᴇʀ ɴᴏᴛ ɪɴ ᴛʜᴇ ᴡᴏʀᴅ
4. ғɪʀsᴛ ᴘᴇʀsᴏɴ ᴛᴏ ɢᴜᴇss ᴄᴏʀʀᴇᴄᴛʟʏ ᴡɪɴs!
5. ᴍᴀxɪᴍᴜᴍ 30 ɢᴜᴇssᴇs ᴘᴇʀ ɢᴀᴍᴇ

**ʙᴀsɪᴄ ᴄᴏᴍᴍᴀɴᴅs:**
• /new - sᴛᴀʀᴛ ᴀ ɴᴇᴡ ɢᴀᴍᴇ
• /end - ᴇɴᴅ ᴄᴜʀʀᴇɴᴛ ɢᴀᴍᴇ (ᴠᴏᴛɪɴɢ ᴏʀ ᴀᴅᴍɪɴ ᴏɴʟʏ)
• /help - sʜᴏᴡ ᴛʜɪs ʜᴇʟᴘ ᴍᴇɴᴜ
• /daily - ᴘʟᴀʏ ᴅᴀɪʟʏ ᴡᴏʀᴅsᴇᴇᴋ (ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ ᴏɴʟʏ)
• /pausedaily - ᴘᴀᴜsᴇ ᴅᴀɪʟʏ ᴍᴏᴅᴇ ᴀɴᴅ ɢᴏ ʙᴀᴄᴋ ᴛᴏ ɴᴏʀᴍᴀʟ ɢᴀᴍᴇs
• /score - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴏʀ ᴏᴛʜᴇʀs ᴘᴏɪɴᴛs
"""
    await cb.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data="help_menu")]]))

@Client.on_callback_query(filters.regex("lb_scores"))
async def lb_scores_callback(client, cb):
    text = """
🏆 **ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ & sᴄᴏʀᴇs**

ᴄʜᴇᴄᴋ ᴡʜᴏ ɪs ʀᴜʟɪɴɢ ᴛʜᴇ ᴡᴏʀᴅsᴇᴇᴋ ᴡᴏʀʟᴅ!

• ᴜsᴇ /leaderboard ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ ᴛᴏ sᴇᴇ ᴛᴏᴘ ᴘʟᴀʏᴇʀs.
• ᴜsᴇ /score ᴛᴏ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴏᴡɴ ᴘᴏɪɴᴛs.
• ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ ᴡɪᴛʜ /score ᴛᴏ sᴇᴇ ᴛʜᴇɪʀ ʀᴀɴᴋ.

ᴘᴏɪɴᴛs ᴀʀᴇ ᴀᴡᴀʀᴅᴇᴅ ʙᴀsᴇᴅ ᴏɴ ʜᴏᴡ ғᴀsᴛ ʏᴏᴜ ɢᴜᴇss ᴛʜᴇ ᴡᴏʀᴅ!
"""
    await cb.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data="help_menu")]]))

@Client.on_callback_query(filters.regex("help_menu"))
async def help_menu_callback(client, cb):
    text = """
▶ **ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs (ᴀᴅᴍɪɴ ᴏɴʟʏ)**

**ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs**
/seekauth – ᴍᴀɴᴀɢᴇ ᴜsᴇʀs ᴡʜᴏ ᴄᴀɴ ᴇɴᴅ ɢᴀᴍᴇs ᴡɪᴛʜᴏᴜᴛ ᴀ ᴠᴏᴛᴇ.

**ᴜsᴀɢᴇ:**
• `/seekauth @username` – ᴀᴜᴛʜᴏʀɪᴢᴇ ᴀ ᴜsᴇʀ
• `/seekauth remove @username` – ʀᴇᴍᴏᴠᴇ ᴀᴜᴛʜᴏʀɪᴢᴀᴛɪᴏɴ
• `/seekauth list` – ʟɪsᴛ ᴀʟʟ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs
• `/rmallauth` – ʀᴇᴍᴏᴠᴇ ᴀʟʟ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs (ɢʀᴏᴜᴘ cleanup)

ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴜsᴇ ᴀ ᴜsᴇʀ ɪᴅ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ɪɴsᴛᴇᴀᴅ ᴏғ `@username`.

**ɢᴀᴍᴇ ᴛᴏᴘɪᴄ (ғᴏʀᴜᴍ ɢʀᴏᴜᴘs)**
/setgametopic – ʀᴇsᴛʀɪᴄᴛ ɢᴀᴍᴇs ᴛᴏ ᴏɴᴇ ᴏʀ ᴍᴏʀᴇ ᴛᴏᴘɪᴄs
ʀᴜɴ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ _ɪɴsɪᴅᴇ ᴛʜᴇ ᴛᴏᴘɪᴄ_ ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ɢᴀᴍᴇs ᴛᴏ ʙᴇ ᴘʟᴀʏᴇᴅ.
ᴀғᴛᴇʀ sᴇᴛᴛɪɴɢ, ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ᴏɴʟʏ ʀᴜɴ ɢᴀᴍᴇs ɪɴ ᴛʜᴀᴛ ᴛᴏᴘɪᴄ.

/unsetgametopic – ʀᴇᴍᴏᴠᴇ ᴛᴏᴘɪᴄ ʀᴇsᴛʀɪᴄᴛɪᴏɴ
**ᴜsᴀɢᴇ:** `/unsetgametopic`
ᴀғᴛᴇʀ ᴜɴsᴇᴛᴛɪɴɢ, ᴛʜᴇ ʙᴏᴛ ᴄᴀɴ ʀᴜɴ ɢᴀᴍᴇs ɪɴ ᴀɴʏ ᴛᴏᴘɪᴄ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ ᴀɢᴀɪɴ.
"""
    buttons = [
        [
            InlineKeyboardButton("ʜᴏᴡ ᴛᴏ ᴘʟᴀʏ", callback_data="how_to_play"), 
            InlineKeyboardButton("ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ & sᴄᴏʀᴇs", callback_data="lb_scores")
        ],
        [
            InlineKeyboardButton("ᴏᴡɴᴇʀ", url="tg://user?id=7589623332")
        ]
    ]
    await cb.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command("score"))
async def get_score(client, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_name = message.reply_to_message.from_user.first_name
    elif len(message.command) > 1:
        try:
            user_id = int(message.command[1])
            user = await client.get_users(user_id)
            user_name = user.first_name
        except:
            return await message.reply_text("❌ **ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ɪᴅ.**")
    else:
        user_id = message.from_user.id
        user_name = message.from_user.first_name

    data = await scores.find_one({"user_id": user_id, "chat_id": message.chat.id})
    score_val = data.get("score", 0) if data else 0
    
    await message.reply_text(f"👤 **ᴜsᴇʀ:** {user_name}\n🏆 **sᴄᴏʀᴇ ᴘᴏɪɴᴛs:** `{score_val}`")
