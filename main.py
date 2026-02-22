import os
from pyrogram import Client, filters
from flask import Flask
from threading import Thread

# Flask for Render Port Binding
app = Flask(__name__)
@app.route('/')
def health_check():
    return "ʙᴏᴛ ɪs ᴀʟɪᴠᴇ ɴx"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# Bot Configuration
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Client(
    "WordSeekBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("ʙᴏᴛ sᴛᴀʀᴛɪɴɢ ɴx...")
    bot.run()
