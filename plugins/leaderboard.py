from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import scores
from datetime import datetime

@Client.on_callback_query(filters.regex(r"lb_(.*)"))
async def leaderboard_handler(client, cb: CallbackQuery):
    lb_type = cb.data.split("_")[1]
    now = datetime.now()
    
    # Filter selection based on button logic
    if lb_type == "month":
        query_type = f"monthly_{now.month}_{now.year}"
        title = "ᴛʜɪs ᴍᴏɴᴛʜ"
    elif lb_type == "year":
        query_type = f"yearly_{now.year}"
        title = "ᴛʜɪs ʏᴇᴀʀ"
    elif lb_type == "today":
        query_type = f"daily_{now.day}_{now.month}_{now.year}"
        title = "ᴛᴏᴅᴀʏ"
    elif lb_type == "week":
        query_type = f"weekly_{now.isocalendar()[1]}_{now.year}"
        title = "ᴛʜɪs ᴡᴇᴇᴋ"
    elif lb_type == "chat":
        query_type = f"chat_{cb.message.chat.id}"
        title = "ᴛʜɪs ᴄʜᴀᴛ"
    else:
        query_type = "all_time"
        title = "ɢʟᴏʙᴀʟ"

    # Database se data nikalna
    top_players = scores.find({"type": query_type}).sort("pts", -1).limit(15)
    
    # Header format matching Photo 1 and 2
    lb_text = f"🏆 **ɢʟᴏʙᴀʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ** 🏆\n\n"
    
    rank = 1
    has_players = False
    async for p in top_players:
        has_players = True
        try:
            user = await client.get_users(p["user_id"])
            name = user.first_name
        except:
            name = "Unknown"
            
        if rank == 1:
            lb_text += f"🥇 {name} - {p['pts']:,} ᴘᴛs\n"
        elif rank == 2:
            lb_text += f"🥈 {name} - {p['pts']:,} ᴘᴛs\n"
        elif rank == 3:
            lb_text += f"🥉 {name} - {p['pts']:,} ᴘᴛs\n"
        else:
            lb_text += f"☀️ {name} - {p['pts']:,} ᴘᴛs\n"
        
        # Separator line after top 3 as seen in screenshot
        if rank == 3:
            lb_text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        rank += 1

    if not has_players:
        lb_text += "ɴᴏ sᴄᴏʀᴇs ғᴏᴜɴᴅ ʏᴇᴛ."

    # Dynamic Tick/Bracket Logic: Jispe click kiya uske aage peeche « » lag jayega
    def get_btn_text(text, current_type):
        return f"« {text} »" if lb_type == current_type else text

    buttons = [
        [
            InlineKeyboardButton(get_btn_text("ɢʟᴏʙᴀʟ", "all"), callback_data="lb_all"), 
            InlineKeyboardButton(get_btn_text("ᴛʜɪs ᴄʜᴀᴛ", "chat"), callback_data="lb_chat")
        ],
        [
            InlineKeyboardButton(get_btn_text("ᴛᴏᴅᴀʏ", "today"), callback_data="lb_today"), 
            InlineKeyboardButton(get_btn_text("ᴛʜɪs ᴡᴇᴇᴋ", "week"), callback_data="lb_week"), 
            InlineKeyboardButton(get_btn_text("« ᴛʜɪs ᴍᴏɴᴛʜ »" if lb_type == "month" else "ᴛʜɪs ᴍᴏɴᴛʜ", "month"), callback_data="lb_month")
        ],
        [
            InlineKeyboardButton(get_btn_text("ᴛʜɪs ʏᴇᴀʀ", "year"), callback_data="lb_year"), 
            InlineKeyboardButton(get_btn_text("ᴀʟʟ ᴛɪᴍᴇ", "all_time"), callback_data="lb_all")
        ],
        [
            InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs ↗️", url="https://t.me/fexionbots"), 
            InlineKeyboardButton("🔄", callback_data=f"lb_{lb_type}"), 
            InlineKeyboardButton("ᴅɪsᴄᴜssɪᴏɴ ↗️", url="https://t.me/EvaraSupportChat")
        ]
    ]
    
    try:
        await cb.edit_message_text(lb_text, reply_markup=InlineKeyboardMarkup(buttons))
    except Exception as e:
        # Agar message same ho to error na de
        print(f"Leaderboard error: {e}")
