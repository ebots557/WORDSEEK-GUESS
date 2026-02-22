from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import scores
from datetime import datetime

@Client.on_callback_query(filters.regex(r"lb_(.*)"))
async def leaderboard_handler(client, cb):
    lb_type = cb.data.split("_")[1]
    now = datetime.now()
    
    # Filter selection based on button
    if lb_type == "month":
        query_type = f"monthly_{now.month}_{now.year}"
        title = "ᴛʜɪs ᴍᴏɴᴛʜ"
    elif lb_type == "year":
        query_type = f"yearly_{now.year}"
        title = "ᴛʜɪs ʏᴇᴀʀ"
    elif lb_type == "all":
        query_type = "all_time"
        title = "ᴀʟʟ ᴛɪᴍᴇ"
    else:
        query_type = "all_time"
        title = "ɢʟᴏʙᴀʟ"

    top_players = scores.find({"type": query_type}).sort("pts", -1).limit(15)
    
    # Header format from Photo 4
    lb_text = f"🏆 **ɢʟᴏʙᴀʟ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ** 🏆\n\n"
    
    # Top 3 Special Icons
    rank = 1
    async for p in top_players:
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
        
        # Add separator like in photo after top 3
        if rank == 3:
            lb_text += "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        rank += 1

    # Buttons matching Photo 4 exactly
    buttons = [
        [InlineKeyboardButton("« ɢʟᴏʙᴀʟ »", callback_data="lb_all"), 
         InlineKeyboardButton("ᴛʜɪs ᴄʜᴀᴛ", callback_data="lb_chat")],
        [InlineKeyboardButton("ᴛᴏᴅᴀʏ", callback_data="lb_today"), 
         InlineKeyboardButton("ᴛʜɪs ᴡᴇᴇᴋ", callback_data="lb_week"), 
         InlineKeyboardButton("« ᴛʜɪs ᴍᴏɴᴛʜ »", callback_data="lb_month")],
        [InlineKeyboardButton("ᴛʜɪs ʏᴇᴀʀ", callback_data="lb_year"), 
         InlineKeyboardButton("ᴀʟʟ ᴛɪᴍᴇ", callback_data="lb_all")],
        [InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs ↗️", url="https://t.me/fexionbots"), 
         InlineKeyboardButton("🔄", callback_data=f"lb_{lb_type}"), 
         InlineKeyboardButton("ᴅɪsᴄᴜssɪᴏɴ ↗️", url="https://t.me/EvaraSupportChat")]
    ]
    
    await cb.edit_message_text(lb_text, reply_markup=InlineKeyboardMarkup(buttons))
