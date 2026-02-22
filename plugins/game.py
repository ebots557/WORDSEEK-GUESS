import asyncio
import random
import requests
import datetime
import os
import time
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database import save_score, scores, is_user_auth # is_user_auth import kiya admin check ke liye

# Game state storage
active_games = {} 

# Owner ID for /end permission
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

# APIs
DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en/"
WORDS_API = "https://api.datamuse.com/words?sp=?????&max=1000"

def get_unlimited_word():
    """Unlimited random 5-letter word fetch karne ke liye logic"""
    try:
        response = requests.get(WORDS_API, timeout=5).json()
        word_list = [w['word'].upper() for w in response if len(w['word']) == 5 and w['word'].isalpha()]
        return random.choice(word_list)
    except Exception as e:
        print(f"Error fetching words: {e}")
        return random.choice(["GLINT", "POWER", "SIGHT", "GUEST", "VOCAL", "GIANT", "SHARP", "LIGHT", "CLEAN", "BRAIN"]).upper()

def is_valid_word(word, target):
    """Check if the word exists in dictionary or is the target word itself"""
    if word.upper() == target.upper():
        return True
    try:
        response = requests.get(f"{DICT_API}{word.lower()}", timeout=3)
        return response.status_code == 200
    except:
        return True 

def get_word_definition(word):
    """Word ka meaning aur pronunciation"""
    try:
        response = requests.get(f"{DICT_API}{word.lower()}", timeout=5).json()
        if isinstance(response, list):
            phonetic = response[0].get("phonetic", f"/{word.lower()}/")
            meanings = response[0].get("meanings", [])
            definition = "ᴅᴇғɪɴɪᴛɪᴏɴ ɴᴏᴛ ғᴏᴜɴᴅ."
            if meanings:
                definition = meanings[0]["definitions"][0].get("definition", definition)
            return phonetic, definition
    except:
        pass
    return f"/{word.lower()}/", "ᴅᴇғɪɴɪᴛɪᴏɴ ɴᴏᴛ ғᴏᴜɴᴅ."

def get_colored_boxes(guess, target):
    """Wordle Algorithm: Half-space logic for perfect box alignment"""
    guess = guess[:5].upper()
    target = target.upper()
    result = ["🟥"] * 5
    target_list = list(target)
    guess_list = list(guess)

    # First pass: Find Green
    for i in range(5):
        if guess_list[i] == target_list[i]:
            result[i] = "🟩"
            target_list[i] = None
            guess_list[i] = None

    # Second pass: Find Yellow
    for i in range(5):
        if guess_list[i] is not None and guess_list[i] in target_list:
            result[i] = "🟨"
            target_list[target_list.index(guess_list[i])] = None
            
    # Single space for half-space look (boxes stay close)
    return " ".join(result)

async def auto_end_game(client, chat_id):
    """Logic to end game if no activity for 10+5 minutes"""
    await asyncio.sleep(600) # 10 Minutes wait
    if chat_id in active_games:
        current_time = time.time()
        if current_time - active_games[chat_id]["last_activity"] >= 600:
            try:
                await client.send_message(chat_id, "ɴᴏ ᴏɴᴇ ᴘʟᴀʏ ᴛʜɪs ɢᴀᴍᴇ, sᴏ ᴛʜɪs ɢᴀᴍᴇ ᴡɪʟʟ ᴇɴᴅ ɪɴ 5 ᴍɪɴᴜᴛᴇs.")
            except:
                pass
            await asyncio.sleep(300) # 5 Minutes more wait
            if chat_id in active_games and time.time() - active_games[chat_id]["last_activity"] >= 900:
                word = active_games[chat_id]["word"]
                del active_games[chat_id]
                try:
                    await client.send_message(chat_id, f"🛑 **ɢᴀᴍᴇ ᴇɴᴅᴇᴅ ᴅᴜᴇ ᴛᴏ ɪɴᴀᴄᴛɪᴠɪᴛʏ!**\nᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: **{word}**")
                except:
                    pass

@Client.on_message(filters.command("new") & (filters.group | filters.private))
async def start_new_game(client, message):
    chat_id = message.chat.id
    if chat_id in active_games:
        return await message.reply_text("ᴀ ɢᴀᴍᴇ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ! ᴇɴᴅ ɪᴛ ᴡɪᴛʜ /end ғɪʀsᴛ.", quote=True)
    
    word = get_unlimited_word()
    max_att = 30
    
    active_games[chat_id] = {
        "word": word,
        "guesses": [],
        "used_words": set(), 
        "attempts": 0,
        "max_attempts": max_att,
        "status": "playing",
        "is_daily": False,
        "last_activity": time.time()
    }
    await message.reply_text(f"🎯 **ᴡᴏʀᴅsᴇᴇᴋ sᴛᴀʀᴛᴇᴅ!**\nɢᴜᴇss ᴛʜᴇ 𝟻-ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ. ʏᴏᴜ ʜᴀᴠᴇ **{max_att}** ᴀᴛᴛᴇᴍᴘᴛs.", quote=True)
    asyncio.create_task(auto_end_game(client, chat_id))

@Client.on_message(filters.command("end"))
async def end_game(client, message):
    chat_id = message.chat.id
    if chat_id not in active_games:
        return await message.reply_text("ɴᴏ ᴀᴄᴛɪᴠᴇ ɢᴀᴍᴇ ᴛᴏ ᴇɴᴅ.", quote=True)
    
    if active_games[chat_id].get("is_daily"):
        return await message.reply_text("ᴛʜɪs ɪs ᴀ ᴅᴀɪʟʏ ɢᴀᴍᴇ. ᴜsᴇ /pausedaily ᴛᴏ sᴛᴏᴘ ɪᴛ.", quote=True)

    user_id = message.from_user.id
    is_auth = False
    
    if user_id == OWNER_ID:
        is_auth = True
    elif message.chat.type == enums.ChatType.PRIVATE:
        is_auth = True 
    else:
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
                is_auth = True
            elif await is_user_auth(chat_id, user_id):
                is_auth = True
        except Exception:
            is_auth = False
            
    if is_auth:
        word = active_games[chat_id]["word"]
        phonetic, meaning = get_word_definition(word)
        del active_games[chat_id]
        end_text = f"🛑 **ɢᴀᴍᴇ ᴇɴᴅᴇᴅ!**\n\n<blockquote>**ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs:** {word}\n**ᴍᴇᴀɴɪɴɢ:** {meaning}</blockquote>"
        await client.send_message(chat_id, end_text, reply_to_message_id=message.id)
    else:
        await message.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴏʀ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴜsᴇʀs ᴄᴀɴ ᴇɴᴅ ᴛʜᴇ ɢᴀᴍᴇ.", quote=True)

@Client.on_message(filters.command("pausedaily") & filters.private)
async def pause_daily(client, message):
    chat_id = message.chat.id
    if chat_id in active_games and active_games[chat_id].get("is_daily"):
        word = active_games[chat_id]["word"]
        del active_games[chat_id]
        await message.reply_text(f"⏸ **ᴅᴀɪʟʏ ɢᴀᴍᴇ ᴘᴀᴜsᴇᴅ!**\nᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs: **{word}**\nsᴛᴀʀᴛ ᴀ ɴᴇᴡ ɢᴀᴍᴇ ᴡɪᴛʜ /new", quote=True)
    else:
        await message.reply_text("ɴᴏ ᴀᴄᴛɪᴠᴇ ᴅᴀɪʟʏ ɢᴀᴍᴇ ᴛᴏ ᴘᴀᴜsᴇ.", quote=True)

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
    game["last_activity"] = time.time()

    if guess in game["used_words"]:
        return await message.reply_text("ᴛʜɪs ɪs ᴀʟʀᴇᴀᴅʏ ɢᴜᴇssᴇᴅ ʙʏ sᴏᴍᴇᴏɴᴇ.", quote=True)
    
    if not is_valid_word(guess, target):
        return await message.reply_text(f"**{guess.lower()}** ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ᴡᴏʀᴅ.", quote=True)
    
    game["used_words"].add(guess)
    
    if guess == target:
        game["status"] = "won"
        pts = max(5, 20 - game["attempts"])
        await save_score(message.from_user.id, chat_id, pts)
        
        # Super Stable Dynamic Reaction Logic
        emojis = ["🎉", "💯", "👀", "❤️", "⚡", "🔥", "🦄", "🕊️", "🏆", "❤️‍🔥", "🍓", "🤗", "🤝", "🗿", "💘"]
        random.shuffle(emojis)
        for emo in emojis:
            try:
                await client.send_reaction(chat_id, message.id, emo)
                break # Reaction successful, exit loop
            except:
                continue # Try next emoji if this one is not allowed
            
        phonetic, meaning = get_word_definition(target)
        
        win_text = f"""
{message.from_user.mention}
**{guess}**

<blockquote>ᴄᴏɴɢʀᴀᴛs! ʏᴏᴜ ɢᴜᴇssᴇᴅ ɪᴛ ᴄᴏʀʀᴇᴄᴛʟʏ.
ᴀᴅᴅᴇᴅ {pts} ᴛᴏ ᴛʜᴇ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ.
sᴛᴀʀᴛ ᴡɪᴛʜ /new

**ᴄᴏʀʀᴇᴄᴛ ᴡᴏʀᴅ:** {target.lower()}
**{target.lower()}** {phonetic}
**ᴍᴇᴀɴɪɴɢ:** {meaning}</blockquote>
"""
        try:
            await client.send_message(chat_id, win_text, reply_to_message_id=message.id)
        except:
            await message.reply_text(win_text) # Safe fallback

        del active_games[chat_id]
        return

    game["attempts"] += 1
    boxes = get_colored_boxes(guess, target)
    game["guesses"].append(f"{boxes}  **{guess}**") 
    
    if game["attempts"] >= game["max_attempts"]:
        try:
            await client.send_message(chat_id, f"❌ ɢᴀᴍᴇ ᴏᴠᴇʀ! ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs **{target}**", reply_to_message_id=message.id)
        except:
            await message.reply_text(f"❌ ɢᴀᴍᴇ ᴏᴠᴇʀ! ᴛʜᴇ ᴡᴏʀᴅ ᴡᴀs **{target}**")
        del active_games[chat_id]
    else:
        history = "\n".join(game["guesses"])
        hint_msg = ""
        
        if game.get("is_daily") or (game["max_attempts"] == 30 and game["attempts"] >= 20):
            _, meaning = get_word_definition(target)
            hint_msg = f"\n\n💡 **ʜɪɴᴛ:** {meaning[:100]}..."

        await message.reply_text(f"{history}{hint_msg}", quote=True)

@Client.on_message(filters.command("daily") & filters.private)
async def daily_game(client, message):
    user_id = message.from_user.id
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    already_played = await scores.find_one({"user_id": user_id, "type": f"daily_played_{today}"})
    if already_played:
        return await message.reply_text("🔒 **ʏᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴘʟᴀʏᴇᴅ ᴛᴏᴅᴀʏ's ᴡᴏʀᴅ!**\nᴄᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ.", quote=True)

    random.seed(today)
    word = get_unlimited_word()
    random.seed()

    if message.chat.id in active_games:
        return await message.reply_text("ᴀ ɢᴀᴍᴇ ɪs ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ! /end ɪᴛ ғɪʀsᴛ.", quote=True)

    active_games[message.chat.id] = {
        "word": word,
        "guesses": [],
        "used_words": set(),
        "attempts": 0,
        "max_attempts": 6,
        "status": "playing",
        "is_daily": True,
        "last_activity": time.time()
    }
    await scores.update_one(
        {"user_id": user_id, "type": f"daily_played_{today}"},
        {"$set": {"played": True, "createdAt": datetime.datetime.now()}},
        upsert=True
    )
    await message.reply_text("🎯 **ᴡᴏʀᴅsᴇᴇᴋ ᴏғ ᴛʜᴇ ᴅᴀʏ sᴛᴀʀᴛᴇᴅ!**\nɢᴜᴇss ᴛʜᴇ ᴜɴɪǫᴜᴇ 𝟻-ʟᴇᴛᴛᴇʀ ᴡᴏʀᴅ. ʏᴏᴜ ʜᴀᴠᴇ 𝟼 ᴀᴛᴛᴇᴍᴘᴛs.", quote=True)
    asyncio.create_task(auto_end_game(client, message.chat.id))
