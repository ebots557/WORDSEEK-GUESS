import asyncio
import random
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from database import save_score

# Game state storage
active_games = {} 

# Dictionary API URL
DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def get_word_definition(word):
    """Word ka meaning aur pronunciation API se nikalne ke liye"""
    try:
        response = requests.get(f"{DICT_API}{word}", timeout=5).json()
        if isinstance(response, list):
            phonetic = response[0].get("phonetic", f"/{word.lower()}/")
            meaning = response[0]["meanings"][0]["definitions"][0].get("definition", "No definition found.")
            example = response[0]["meanings"][0]["definitions"][0].get("example", "No example available.")
            return phonetic, meaning, example
    except:
        pass
    return f"/{word.lower()}/", "ᴅᴇғɪɴɪᴛɪᴏɴ ɴᴏᴛ ғᴏᴜɴᴅ.", "ɴ/ᴀ"

def get_colored_boxes(guess, target):
    result = ""
    for i in range(5):
        if guess[i] == target[i]:
            result += "🟩"
        elif guess[i] in target:
            result += "🟨"
        else:
            result += "🟥"
    return result

@Client.on_message(filters.command("new"))
async def start_new_game(client, message):
    chat_id = message.chat.id
    if chat_id in active_games:
        return await message.reply_text("ᴀ ɢᴀᴍᴇ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ! ᴇɴᴅ ɪᴛ ᴡɪᴛʜ /end ғɪʀsᴛ.")
    
    # Unlimited words ke liye hum kisi bhi word list file ka use kar sakte hain
    # Yahan hum ek sample list de rahe hain, aap badi file bhi load kar sakte hain
    WORDS = ["APPLE", "GLINT", "POWER", "SIGHT", "GUEST", "VOCAL", "GIANT", "SHARP", "LIGHT", "CLEAN"]
    word = random.choice(WORDS).upper()
    
    active_games[chat_id] = {
        "word": word,
        "guesses": [],
        "attempts": 0,
        "status": "playing"
    }
    await message.reply_text("🎯 **ᴡᴏʀᴅsᴇᴇᴋ sᴛᴀʀᴛᴇᴅ!**\nɢᴜᴇss ᴛʜᴇ 𝟻-ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ. ʏᴏᴜ ʜᴀᴠᴇ 𝟹𝟶 ᴀᴛᴛᴇᴍᴘᴛs.")

@Client.on_message(filters.text & filters.group & ~filters.command(["start", "help", "new", "end", "leaderboard", "score"]))
async def handle_guess(client, message):
    chat_id = message.chat.id
    if chat_id not in active_games or active_games[chat_id]["status"] != "playing":
        return

    guess = message.text.upper().strip()
    
    if len(guess) != 5 or not guess.isalpha():
        return 
    
    game = active_games[chat_id]
    target = game["word"]
    
    # Word check API se (Taki valid word hi accept ho)
    # Note: Speed ke liye aap ye validation skip bhi kar sakte hain
    
    if guess == target:
        game["status"] = "won"
        pts = max(5, 20 - game["attempts"])
        await save_score(message.from_user.id, pts)
        
        # Winner Reaction
        try:
            await message.react("🎉", "👀", "❤️")
        except:
            pass
            
        phonetic, meaning, example = get_word_definition(target)
        
        win_text = f"""
{message.from_user.mention}
**{guess}**

ᴄᴏɴɢʀᴀᴛs! ʏᴏᴜ ɢᴜᴇssᴇᴅ ɪᴛ ᴄᴏʀʀᴇᴄᴛʟʏ.
ᴀᴅᴅᴇᴅ {pts} ᴛᴏ ᴛʜᴇ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ.
sᴛᴀʀᴛ ᴡɪᴛʜ /new

<blockquote>
**ᴄᴏʀʀᴇᴄᴛ ᴡᴏʀᴅ:** {target.lower()}
**{target.lower()}** {phonetic}
**ᴍᴇᴀɴɪɴɢ:** {meaning}
**ᴇxᴀᴍᴘʟᴇ:** {example}
</blockquote>
"""
        await message.reply_text(win_text)
        del active_games[chat_id]
        return

    # Wrong guess logic
    game["attempts"] += 1
    boxes = get_colored_boxes(guess, target)
    game["guesses"].append(f"{boxes} **{guess}**")
    
    if game["attempts"] >= 30:
        await message.reply_text(f"❌ ɢᴀᴍᴇ ᴏᴠᴇʀ! ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs **{target}**")
        del active_games[chat_id]
    else:
        history = "\n".join(game["guesses"])
        await message.reply_text(f"{history}\n\n`{30 - game['attempts']} attempts remaining`")

@Client.on_message(filters.command("daily") & filters.private)
async def daily_game(client, message):
    # Daily logic: Ek fixed seed based on Date
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    random.seed(today)
    # Baki logic /new jaisa hi rahega...
    await message.reply_text("🎯 **ᴡᴏʀᴅsᴇᴇᴋ ᴏғ ᴛʜᴇ ᴅᴀʏ sᴛᴀʀᴛᴇᴅ!**\nɢᴜᴇss ᴛʜᴇ 𝟻-ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ. ʏᴏᴜ ʜᴀᴠᴇ 𝟼 ᴀᴛᴛᴇᴍᴘᴛs. ɢᴏᴏᴅ ʟᴜᴄᴋ!")
