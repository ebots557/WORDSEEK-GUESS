from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import scores
from datetime import datetime
import os

# Owner ID environmental variables se uthayega
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

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
            InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/naxeyi")
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
• /help - sʜᴏᴡ ᴛʜɪs ʜᴇʟᴘ ᴍᴇɴᴜ, /score - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴏʀ ᴏᴛʜᴇʀs ᴛᴏᴛᴀʟ sᴄᴏʀᴇ
• /daily - ᴘʟᴀʏ ᴅᴀɪʟʏ ᴡᴏʀᴅsᴇᴇᴋ (ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ ᴏɴʟʏ)
• /pausedaily - ᴘᴀᴜsᴇ ᴅᴀɪʟʏ ᴍᴏᴅᴇ ᴀɴᴅ ɢᴏ ʙᴀᴄᴋ ᴛᴏ ɴᴏʀᴍᴀʟ ɢᴀᴍᴇs
"""
    await cb.edit_message_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data="help_menu")]]))

@Client.on_callback_query(filters.regex("lb_scores"))
async def lb_scores_callback(client, cb):
    # Leaderboard trigger logic
    await cb.answer()
    await cb.message.edit_text(
        "🏆 **ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ᴍᴇɴᴜ**\n\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴏᴘᴇɴ ᴛʜᴇ ɢʟᴏʙᴀʟ ᴏʀ ᴄʜᴀᴛ-sᴘᴇᴄɪꜰɪᴄ sᴛᴀᴛɪsᴛɪᴄs.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✨ ᴏᴘᴇɴ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ✨", callback_data="lb_global_month")
        ], [
            InlineKeyboardButton("« ʙᴀᴄᴋ", callback_data="help_menu")
        ]])
    )

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
            InlineKeyboardButton("ᴏᴡɴᴇʀ", url="https://t.me/naxeyi")
        ]
    ]
    await cb.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command("score"))
async def score_cmd(client, message):
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            user_input = message.command[1]
            if user_input.isdigit():
                target_user = await client.get_users(int(user_input))
            else:
                target_user = await client.get_users(user_input)
        except Exception:
            return await message.reply_text("❌ **ᴄᴏᴜʟᴅ ɴᴏᴛ ꜰɪɴᴅ ᴛʜᴀᴛ ᴜsᴇʀ.**")
    else:
        target_user = message.from_user

    # Database query: All Time Global Points Only
    user_data = await scores.find_one({"user_id": target_user.id, "type": "all_time", "chat_id": "global"})
    total_pts = user_data.get("pts", 0) if user_data else 0

    await message.reply_text(
        f"👤 **ᴜsᴇʀ:** {target_user.mention}\n"
        f"🏆 **ᴛᴏᴛᴀʟ sᴄᴏʀᴇ ᴀʟʟ ᴛʜᴇ ᴛɪᴍᴇ:** `{total_pts:,} ᴘᴛs` (ᴀʟʟ ᴛɪᴍᴇ)"
    )
