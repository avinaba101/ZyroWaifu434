# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

import time
import random
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import Message

# TEAMZYRO से आपके जरूरी कलेक्टर्स और डेटाबेस इम्पोर्ट हो रहे हैं
from TEAMZYRO import app, collection, last_characters, first_correct_guesses

log = "-1002155818429"

async def delete_message(client: Client, chat_id: int, message_id: int):
    await asyncio.sleep(300)  # 5 minutes (300 seconds)
    try:
        await client.delete_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error deleting message: {e}")

RARITY_WEIGHTS = {
    "⚪️ Common": (40, True),
    "🟣 Rare": (20, True),
    "🟡 Legendary": (12, True),
    "🟢 Medium": (10, True),
    "💮 Special Edition": (8, True),
    "🔮 Limited Edition": (6, True),
    "💸 Premium Edition": (4, True),
    "🌤 Summer": (3, False),
    "🎐 Celestial": (2.5, True),
    "❄️ Winter": (2, False),
    "💝 Valentine": (2, False),
    "🎃 Halloween": (1.8, False),
    "🎄 Christmas Special": (1.5, False),
    "🪐 Omniversal": (1.2, True),
    "🎭 Cosplay Master 🎭": (1, True),
    "🧧 Events": (0.8, False),
    "🎗️ AMV Edition": (0.5, False),
    "🌧 Rainy": (2.0, False),
}

async def send_image(client: Client, message: Message) -> None:
    chat_id = message.chat.id

    # Allowed rarities की लिस्ट बनाना
    allowed_rarities = [k for k, v in RARITY_WEIGHTS.items() if v[1]]

    # Fetch characters from MongoDB matching rarities
    all_characters = await collection.find({"rarity": {"$in": allowed_rarities}}).to_list(length=None)

    if not all_characters:
        await client.send_message(chat_id, "No characters found with allowed rarities in the database.")
        return

    # Filter out valid characters
    available_characters = [
        c for c in all_characters 
        if 'id' in c and c.get('rarity') is not None
    ]

    if not available_characters:
        await client.send_message(chat_id, "No available characters with the allowed rarities.")
        return

    # Weighted random selection
    cumulative_weights = []
    cumulative_weight = 0
    for character in available_characters:
        cumulative_weight += RARITY_WEIGHTS.get(character.get('rarity'), (1, False))[0]
        cumulative_weights.append(cumulative_weight)

    rand = random.uniform(0, cumulative_weight)
    selected_character = None
    for i, character in enumerate(available_characters):
        if rand <= cumulative_weights[i]:
            selected_character = character
            break

    if not selected_character:
        selected_character = random.choice(available_characters)

    # बग फिक्स: चुनी हुई कैरेक्टर इन्फो को सही डिक्शनरी में सेव करना
    last_characters[chat_id] = dict(selected_character)
    last_characters[chat_id]['timestamp'] = time.time()
    
    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    caption_text = f"""✨ A {selected_character['rarity']} Character Appears! ✨
🔍 Use /guess to claim this mysterious character!
💫 Hurry, before someone else snatches them!"""

    # Check if the character has a video URL or Image
    if 'vid_url' in selected_character and selected_character['vid_url']:
        sent_message = await client.send_video(
            chat_id=chat_id,
            video=selected_character['vid_url'],
            caption=caption_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        sent_message = await client.send_photo(
            chat_id=chat_id,
            photo=selected_character['img_url'],
            caption=caption_text,
            parse_mode=enums.ParseMode.MARKDOWN
        )

    # Schedule message deletion after 5 minutes safely using Pyrogram client
    asyncio.create_task(delete_message(client, chat_id, sent_message.id))
