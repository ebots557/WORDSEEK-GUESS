import os
from dotenv import load_dotenv

# Local testing ke liye .env file load karega
load_dotenv()

class Config:
    # --- Telegram API Config ---
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
    # --- Database Config ---
    MONGO_URL = os.environ.get("MONGO_URL", "")
    
    # --- Owner & Logs ---
    OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
    LOG_GROUP = int(os.environ.get("LOG_GROUP", "0")) # Optional: for logs
    
    # --- Bot Appearance (Nx Style) ---
    BOT_NAME = "ᴡᴏʀᴅsᴇᴇᴋ ɴx"
    SUPPORT_CHAT = "EvaraSupportChat" # From screenshot
    UPDATE_CHNL = "Fexionbots"     # From screenshot
    
    # --- Game Settings ---
    MAX_GUESSES = 30 # For normal games
    DAILY_GUESSES = 6 # For daily mode
    
    # --- Admin / Auth Defaults ---
    # In-memory auth list (Reset hone par mongo se load hoga)
    AUTHORIZED_USERS = [OWNER_ID] 
    GAME_TOPICS = {} # {chat_id: [topic_ids]}

# Instance banakar export karna
cfg = Config()
