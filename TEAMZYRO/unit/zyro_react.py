# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

import random
from pyrogram import Client
from TEAMZYRO import app

emojis = ["🇦🇷", "😘", "🇧🇷", "🔥", "🥰", "🌚", "💘", "🇵🇹", "🤯", "⚡️", "🏆", "🤭", "🎉"]

async def react_to_message(chat_id: int, message_id: int):
    try:
        # लिस्ट से रैंडम इमोजी चुनना
        random_emoji = random.choice(emojis)
        
        # Pyrogram का इन-बिल्ट एसिंक फ़ंक्शन जो बिना बोट को ब्लॉक किए रिएक्शन लगाता है
        await app.send_reaction(
            chat_id=chat_id,
            message_id=message_id,
            reaction=random_emoji
        )
        print("Reaction set successfully via Pyrogram!")
        
    except Exception as e:
        print(f"Failed to set reaction: {e}")
