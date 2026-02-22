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
        "used_words": set(), # Duplicate word tracking
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

    user_id = message.from_user.id
    is_auth = False
    
    if message.chat.type == "private":
        is_auth = True # DM me koi bhi end kar sake
    else:
        # Group me Admin, Creator ya Owner
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in ["creator", "administrator"] or user_id == OWNER_ID:
            is_auth = True
            
    if is_auth:
        word = active_games[chat_id]["word"]
        del active_games[chat_id]
        await message.reply_text(f"🛑 **ɢᴀᴍᴇ ᴇɴᴅᴇᴅ!**\nᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: **{word}**")
    else:
        await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇɴᴅ ᴛʜᴇ ɢᴀᴍᴇ ɪɴ ɢʀᴏᴜᴘs.")

@Client.on_message(filters.text & (filters.group | filters.private) & ~filters.command(["start", "help", "new", "end", "leaderboard", "score", "daily", "pausedaily", "seekauth", "setgametopic", "unsetgametopic"]))
async def handle_guess(client, message):
    chat_id = message.chat.id
    if chat_id not in active_games or active_games[chat_id]["status"] != "playing":
        return

    guess = message.text.upper().strip()
    
    if len(guess) != 5 or not guess.isalpha():
        return 
    
    game = active_games[chat_id]
    target = game["word"]

    # Already guessed check
    if guess in game["used_words"]:
        return await message.reply_text("ᴛʜɪs ɪs ᴀʟʀᴇᴀᴅʏ ɢᴜᴇssᴇᴅ ʙʏ sᴏᴍᴇᴏɴᴇ.")
    
    if not is_valid_word(guess):
        return await message.reply_text(f"**{guess.lower()}** is not a valid word.")
    
    game["used_words"].add(guess)
    
    if guess == target:
        game["status"] = "won"
        pts = max(5, 20 - game["attempts"])
        # Global points add (DM logic included)
        await save_score(message.from_user.id, pts)
        
        # Reaction logic fixed
        reactions = ["🎉", "🏆", "🔥", "⚡️", "🤩"]
        try:
            await client.send_reaction(chat_id, message.id, random.choice(reactions))
        except Exception:
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

    game["attempts"] += 1
    boxes = get_colored_boxes(guess, target)
    game["guesses"].append(f"{boxes}  **{guess}**")
    
    if game["attempts"] >= game["max_attempts"]:
        await message.reply_text(f"❌ ɢᴀᴍᴇ ᴏᴠᴇʀ! ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs **{target}**")
        del active_games[chat_id]
    else:
        history = "\n".join(game["guesses"])
        
        # 27 attempts ke baad Hint logic (Group only)
        hint_msg = ""
        if game["max_attempts"] == 30 and game["attempts"] >= 27:
            _, meaning, _ = get_word_definition(target)
            hint_msg = f"\n\n💡 **ʜɪɴᴛ:** {meaning[:50]}..." # Meaning se ishara milega

        # Attempt count spam hataya, sirf history bhejega
        await message.reply_text(f"{history}{hint_msg}", quote=True)

@Client.on_message(filters.command("daily") & filters.private)
async def daily_game(client, message):
    today = datetime.date.today().strftime("%Y-%m-%d")
    random.seed(today)
    
    word = get_unlimited_word()
    random.seed()

    if message.chat.id in active_games:
        return await message.reply_text("ᴀ ɢᴀᴍᴇ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ! /end ɪᴛ ғɪʀsᴛ.")

    active_games[message.chat.id] = {
        "word": word,
        "guesses": [],
        "used_words": set(),
        "attempts": 0,
        "max_attempts": 6,
        "status": "playing",
        "is_daily": True
    }
    
    await message.reply_text("🎯 **ᴡᴏʀᴅsᴇᴇᴋ ᴏғ ᴛʜᴇ ᴅᴀʏ sᴛᴀʀᴛᴇᴅ!**\nɢᴜᴇss ᴛʜᴇ 𝟻-ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ. ʏᴏᴜ ʜᴀᴠᴇ 𝟼 ᴀᴛᴛᴇᴍᴘᴛs. ɢᴏᴏᴅ ʟᴜᴄᴋ!")
