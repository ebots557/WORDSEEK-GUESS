import asyncio
import random
import requests
import datetime
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import save_score

# Game state storage
active_games = {} 

# Owner ID for /end permission
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

# APIs
DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"
# Hazaron random 5-letter words fetch karne ke liye API
WORDS_API = "https://api.datamuse.com/words?sp=?????&max=1000"

def get_unlimited_word():
    """Unlimited random 5-letter word fetch karne ke liye logic"""
    try:
        response = requests.get(WORDS_API, timeout=5).json()
        # Sirf wahi words filter karna jo 5 letter ke hain aur alphabetic hain
        word_list = [w['word'].upper() for w in response if len(w['word']) == 5 and w['word'].isalpha()]
        return random.choice(word_list)
    except Exception as e:
        # Fallback words agar API down ho jaye taaki game crash na ho
        print(f"Error fetching words: {e}")
        return random.choice(["GLINT", "POWER", "SIGHT", "GUEST", "VOCAL", "GIANT", "SHARP", "LIGHT", "CLEAN", "BRAIN"]).upper()

def is_valid_word(word):
    """Check if the word exists in dictionary (Screenshot 6 logic)"""
    try:
        response = requests.get(f"{DICT_API}{word.lower()}", timeout=3)
        return response.status_code == 200
    except:
        return True # Safety check: agar API down ho to game rukne na de

def get_word_definition(word):
    """Word ka meaning aur pronunciation (Screenshot 5 logic)"""
    try:
        response = requests.get(f"{DICT_API}{word.lower()}", timeout=5).json()
        if isinstance(response, list):
            phonetic = response[0].get("phonetic", f"/{word.lower()}/")
            meanings = response[0].get("meanings", [])
            definition = "ᴅᴇғɪɴɪᴛɪᴏɴ ɴᴏᴛ ғᴏᴜɴᴅ."
            example = "ɴᴏ ᴇxᴀᴍᴘʟᴇ ᴀᴠᴀɪʟᴀʙʟᴇ."
            if meanings:
                definition = meanings[0]["definitions"][0].get("definition", definition)
                example = meanings[0]["definitions"][0].get("example", example)
            return phonetic, definition, example
    except:
        pass
    return f"/{word.lower()}/", "ᴅᴇғɪɴɪᴛɪᴏɴ ɴᴏᴛ ғᴏᴜɴᴅ.", "ɴ/ᴀ"

def get_colored_boxes(guess, target):
    """Grid logic with gap for premium look"""
    result = ""
    for i in range(5):
        if guess[i] == target[i]:
            result += "🟩"
        elif guess[i] in target:
            result += "🟨"
        else:
            result += "🟥"
        result += " " # Ye gap box ko mix hone se bachayega
    return result.strip()

@Client.on_message(filters.command("new") & (filters.group | filters.private))
async def start_new_game(client, message):
    chat_id = message.chat.id
    if chat_id in active_games:
        return await message.reply_text("ᴀ ɢᴀᴍᴇ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ! ᴇɴᴅ ɪᴛ ᴡɪᴛʜ /end ғɪʀsᴛ.")
    
    # Unlimited words logic call
    word = get_unlimited_word()
    
    # Attempts decide: Group me 30, Private me 6
    max_att = 30 if message.chat.type != "private" else 6
    
    active_games[chat_id] = {
        "word": word,
        "guesses": [],
        "attempts": 0,
        "max_attempts": max_att,
        "status": "playing"
    }
    await message.reply_text(f"🎯 **ᴡᴏʀᴅsᴇᴇᴋ sᴛᴀʀᴛᴇᴅ!**\nɢᴜᴇss ᴛʜᴇ 𝟻-ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ. ʏᴏᴜ ʜᴀᴠᴇ **{max_att}** ᴀᴛᴛᴇᴍᴘᴛs.")

@Client.on_message(filters.command("end"))
async def end_game(client, message):
    chat_id = message.chat.id
    if chat_id not in active_games:
        return await message.reply_text("ɴᴏ ᴀᴄᴛɪᴠᴇ ɢᴀᴍᴇ ᴛᴏ ᴇɴᴅ.")

    # Permissions: Only Admin, Authorized User, or Owner
    user_id = message.from_user.id
    is_auth = False
    
    if message.chat.type == "private":
        is_auth = True
    else:
        member = await client.get_chat_member(chat_id, user_id)
        # Check if Admin or Owner
        if member.status in ["creator", "administrator"] or user_id == OWNER_ID:
            is_auth = True
            
    if is_auth:
        word = active_games[chat_id]["word"]
        del active_games[chat_id]
        await message.reply_text(f"🛑 **ɢᴀᴍᴇ ᴇɴᴅᴇᴅ!**\nᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: **{word}**")
    else:
        await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴏʀ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ᴄᴀɴ ᴇɴᴅ ᴛʜᴇ ɢᴀᴍᴇ.")

@Client.on_message(filters.text & (filters.group | filters.private) & ~filters.command(["start", "help", "new", "end", "leaderboard", "score", "daily", "pausedaily", "seekauth", "setgametopic", "unsetgametopic"]))
async def handle_guess(client, message):
    chat_id = message.chat.id
    if chat_id not in active_games or active_games[chat_id]["status"] != "playing":
        return

    guess = message.text.upper().strip()
    
    # length aur characters check
    if len(guess) != 5 or not guess.isalpha():
        return 
    
    # Galt word validation (Screenshot 6 logic: invalid word accept nahi karega)
    if not is_valid_word(guess):
        return await message.reply_text(f"**{guess.lower()}** is not a valid word.")
    
    game = active_games[chat_id]
    target = game["word"]
    
    if guess == target:
        game["status"] = "won"
        pts = max(5, 20 - game["attempts"])
        await save_score(message.from_user.id, pts)
        
        # Winner Reactions Fix
        reactions = ["🎉", "🏆", "🔥", "⚡️", "🤩"]
        try:
            await client.send_reaction(chat_id, message.id, random.choice(reactions))
        except:
            pass 
            
        phonetic, meaning, example = get_word_definition(target)
        
        # Exact text jaisa photo me hai
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

    # Wrong guess logic (Attempts update aur grid show karna)
    game["attempts"] += 1
    boxes = get_colored_boxes(guess, target)
    game["guesses"].append(f"{boxes}  **{guess}**")
    
    if game["attempts"] >= game["max_attempts"]:
        await message.reply_text(f"❌ ɢᴀᴍᴇ ᴏᴠᴇʀ! ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs **{target}**")
        del active_games[chat_id]
    else:
        # Premium Look: Har guess par poora grid bhejte hain bina bar bar reply kiye (optional: edit logic)
        history = "\n".join(game["guesses"])
        await message.reply_text(f"{history}\n\n`{game['max_attempts'] - game['attempts']} attempts remaining`", quote=True)

@Client.on_message(filters.command("daily") & filters.private)
async def daily_game(client, message):
    # Daily logic: Date ke basis pe seed set karna taaki har user ko same word mile
    today = datetime.date.today().strftime("%Y-%m-%d")
    random.seed(today)
    
    word = get_unlimited_word()
    random.seed() # Reset seed for other functions

    if message.chat.id in active_games:
        return await message.reply_text("ᴀ ɢᴀᴍᴇ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ! /end ɪᴛ ғɪʀsᴛ.")

    active_games[message.chat.id] = {
        "word": word,
        "guesses": [],
        "attempts": 0,
        "max_attempts": 6,
        "status": "playing",
        "is_daily": True
    }
    
    # Screenshot 7 text logic
    await message.reply_text("🎯 **ᴡᴏʀᴅsᴇᴇᴋ ᴏғ ᴛʜᴇ ᴅᴀʏ sᴛᴀʀᴛᴇᴅ!**\nɢᴜᴇss ᴛʜᴇ 𝟻-ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ. ʏᴏᴜ ʜᴀᴠᴇ 𝟼 ᴀᴛᴛᴇᴍᴘᴛs. ɢᴏᴏᴅ ʟᴜᴄᴋ!")
