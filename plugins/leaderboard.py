from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import scores
from datetime import datetime

# --- DATABASE SAVING LOGIC WITH AUTO-CLEAN ---
async def save_score_logic(user_id, chat_id, pts):
    now = datetime.now()
    
    # Current keys
    periods = {
        "daily": f"daily_{now.day}_{now.month}_{now.year}",
        "weekly": f"weekly_{now.isocalendar()[1]}_{now.year}",
        "monthly": f"monthly_{now.month}_{now.year}",
        "yearly": f"yearly_{now.year}",
        "all_time": "all_time"
    }
    
    # Logic to delete OLD data (Cleaning)
    # Hum sirf current keys ko chhod kar baaki sab delete kar denge 
    # except 'all_time' type.
    for p_type, p_key in periods.items():
        if p_type != "all_time":
            # Purana data delete karo jo current key se match nahi karta
            await scores.delete_many({
                "type": {"$regex": f"^{p_type}_"}, 
                "type": {"$ne": p_key}
            })

    for p_type, p_key in periods.items():
        # Global Update
        await scores.update_one(
            {"user_id": user_id, "type": p_key, "chat_id": "global"},
            {"$inc": {"pts": pts}},
            upsert=True
        )
        # Group Specific Update
        await scores.update_one(
            {"user_id": user_id, "type": p_key, "chat_id": chat_id},
            {"$inc": {"pts": pts}},
            upsert=True
        )

# --------------------------------------------------------------------------

@Client.on_message(filters.command("leaderboard"))
async def leaderboard_cmd(client, message):
    # Default initial view: Global + This Month
    await message.reply_text(
        "🏆 **ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ʟᴏᴀᴅɪɴɢ...**",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✨ ᴏᴘᴇɴ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ ✨", callback_data="lb_global_month")
        ]])
    )

@Client.on_callback_query(filters.regex(r"lb_(.*)"))
async def leaderboard_handler(client, cb: CallbackQuery):
    data = cb.data.split("_")
    scope = data[1]   # 'global' or 'chat'
    period = data[2]  # 'today', 'week', 'month', 'year', 'all'
    
    now = datetime.now()
    current_chat = cb.message.chat.id
    
    # Map periods to DB keys
    period_map = {
        "today": f"daily_{now.day}_{now.month}_{now.year}",
        "week": f"weekly_{now.isocalendar()[1]}_{now.year}",
        "month": f"monthly_{now.month}_{now.year}",
        "year": f"yearly_{now.year}",
        "all": "all_time"
    }
    
    query_type = period_map.get(period, "all_time")
    
    # Filter for Global or specific Chat
    db_chat_id = "global" if scope == "global" else current_chat
    title = "ɢʟᴏʙᴀʟ" if scope == "global" else "ᴛʜɪs ᴄʜᴀᴛ"

    # Database Fetch - Limited to Top 15
    top_players = scores.find({"type": query_type, "chat_id": db_chat_id}).sort("pts", -1).limit(15)
    
    lb_text = f"🏆 **{title} ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ** 🏆\n\n"
    
    rank = 1
    has_players = False
    
    async for p in top_players:
        try:
            # User mention logic
            user = await client.get_users(p["user_id"])
            name = user.mention
            has_players = True
        except:
            # Cleanup deleted accounts
            await scores.delete_many({"user_id": p["user_id"]})
            continue
            
        if rank == 1:
            lb_text += f"🥇 {name} - {p['pts']:,} ᴘᴛs\n"
        elif rank == 2:
            lb_text += f"🥈 {name} - {p['pts']:,} ᴘᴛs\n"
        elif rank == 3:
            lb_text += f"🥉 {name} - {p['pts']:,} ᴘᴛs\n"
        else:
            lb_text += f"☀️ {name} - {p['pts']:,} ᴘᴛs\n"
        
        if rank == 3:
            lb_text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        rank += 1

    if not has_players:
        lb_text += "ɴᴏ sᴄᴏʀᴇs ғᴏᴜɴᴅ ғᴏʀ ᴛʜɪs sᴇᴄᴛɪᴏɴ."

    # Button Bracket Logic
    def get_scope_btn(txt, target):
        return f"« {txt} »" if scope == target else txt

    def get_period_btn(txt, target):
        return f"« {txt} »" if period == target else txt

    buttons = [
        [
            InlineKeyboardButton(get_scope_btn("ɢʟᴏʙᴀʟ", "global"), callback_data=f"lb_global_{period}"),
            InlineKeyboardButton(get_scope_btn("ᴛʜɪs ᴄʜᴀᴛ", "chat"), callback_data=f"lb_chat_{period}")
        ],
        [
            InlineKeyboardButton(get_period_btn("ᴛᴏᴅᴀʏ", "today"), callback_data=f"lb_{scope}_today"),
            InlineKeyboardButton(get_period_btn("ᴛʜɪs ᴡᴇᴇᴋ", "week"), callback_data=f"lb_{scope}_week"),
            InlineKeyboardButton(get_period_btn("ᴛʜɪs ᴍᴏɴᴛʜ", "month"), callback_data=f"lb_{scope}_month")
        ],
        [
            InlineKeyboardButton(get_period_btn("ᴛʜɪs ʏᴇᴀʀ", "year"), callback_data=f"lb_{scope}_year"),
            InlineKeyboardButton(get_period_btn("ᴀʟʟ ᴛɪᴍᴇ", "all"), callback_data=f"lb_{scope}_all")
        ],
        [
            InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs ↗️", url="https://t.me/fexionbots"),
            InlineKeyboardButton("🔄", callback_data=cb.data),
            InlineKeyboardButton("ᴡᴏʀᴅ ɢᴜᴇss ᴄʜᴀᴛ ↗️", url="https://t.me/WordguessnxChat")
        ]
    ]
    
    try:
        await cb.edit_message_text(lb_text, reply_markup=InlineKeyboardMarkup(buttons))
    except:
        pass
