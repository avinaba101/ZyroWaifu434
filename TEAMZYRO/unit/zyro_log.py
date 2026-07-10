# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

import asyncio
from pyrogram import Client, enums
from TEAMZYRO import app

# यहाँ अपने लॉग चैनल या ग्रुप की सही ID डालें (जैसे: -1002155818429)
LOG_CHAT_ID = -1002155818429  

BOT_USERNAME = "@Gaming_X_World_Bot"
OWNER_NAME = "@sukuna_dev"
IMAGE_URL = "https://files.catbox.moe/ehv507.jpeg"

async def send_start_message():
    try:
        caption = (
            f"🤖 <b>Bot has started successfully!</b>\n\n"
            f"🧑‍💻 <b>Owner:</b> {OWNER_NAME}\n\n"
            f"🚀 <b>Status:</b> All systems are operational!"
        )
        
        # Pyrogram का एसिंक्रोनस मेथड जो बिना बोट को ब्लॉक किए फोटो भेजेगा
        await app.send_photo(
            chat_id=LOG_CHAT_ID,
            photo=IMAGE_URL,
            caption=caption,
            parse_mode=enums.ParseMode.HTML
        )
        print("Start message sent successfully via Pyrogram!")
        
    except Exception as e:
        print(f"Failed to send start message: {e}")
