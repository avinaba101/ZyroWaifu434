# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

from TEAMZYRO import *
from html import escape
import asyncio
import time
import random  
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from datetime import datetime, timezone

# ⏱️ COMMAND SPAM CONTROL
GUESS_COOLDOWN_TIME = 8  
guess_cooldowns = {}

# 🎭 RANDOM STICKERS LIST
STICKERS = [
    "CAACAgIAAxkBAAEFzlljF2...", 
    "CAACAgIAAxkBAAEFzltjF2...", 
    "CAACAgIAAxkBAAEFzl1jF2...", 
    "CAACAgIAAxkBAAEFzl9jF2..."
]

@app.on_message(filters.command(["guess", "protecc", "collect", "grab", "hunt"]) & filters.group)
async def guess(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None
    
    if not user_id:
        return
        
    current_time = time.time()
    today = datetime.now(timezone.utc).date()

    # COOLDOWN CHECK
    if user_id in guess_cooldowns:
        time_passed = current_time - guess_cooldowns[user_id]
        if time_passed < GUESS_COOLDOWN_TIME:
            remaining = int(GUESS_COOLDOWN_TIME - time_passed)
            try:
                await message.reply_text(f"⚠️ Slow down! Wait {remaining}s.")
            except:
                pass
            return

    if chat_id not in last_characters or 'name' not in last_characters.get(chat_id, {}):
        await message.reply_text("❌ Character Guess not available for this chat.")
        return

    if chat_id in first_correct_guesses:
        await message.reply_text("❌ This character has already been guessed!")
        return

    guess_word = ' '.join(message.command[1:]).lower().strip() if len(message.command) > 1 else ''
    
    if not guess_word:
        await message.reply_text("⚠️ Please provide a character name.")
        return

    guess_cooldowns[user_id] = current_time
    name_parts = last_characters[chat_id]['name'].lower().split()
    
    if sorted(name_parts) == sorted(guess_word.split()) or any(part == guess_word for part in name_parts):
        first_correct_guesses[chat_id] = user_id
        
        for task in asyncio.all_tasks():
            if task.get_name() == f"expire_session_{chat_id}":
                task.cancel()
                break

        grabbed_character = last_characters[chat_id]

        # 💾 DATABASE ME DATA ADD KARNA (100% SAFE - KUCH DELETE NAHI HOGA YAHAN SE)
        user_data = await user_collection.find_one({'id': user_id})
        new_balance = (user_data.get('balance', 0) if user_data else 0) + 40
        
        await user_collection.update_one(
            {'id': user_id},
            {
                '$set': {
                    'username': message.from_user.username,
                    'first_name': message.from_user.first_name,
                    'balance': new_balance
                },
                '$push': {'characters': grabbed_character} # Harem me character humesha ke liye safe save ho gaya
            },
            upsert=True
        )

        group_name = message.chat.title or f"Group_{chat_id}"
        await top_global_groups_collection.update_one(
            {'group_id': str(chat_id)},
            {
                '$set': {'group_name': group_name},
                '$inc': {'count': 1}
            },
            upsert=True
        )

        # 🗑️ ONLY GROUP CHAT SE IMAGE DELETE KARNA (DATABASE SE KOI LENADENA NAHI)
        try:
            async for history_msg in client.get_chat_history(chat_id, limit=35):
                if history_msg.from_user and history_msg.from_user.id == client.me.id:
                    if history_msg.photo or history_msg.document:
                        await history_msg.delete() # Sirf group screen se photo delete hogi
                        break
        except Exception as del_err:
            print(f"Group chat deletion failed: {del_err}")

        # 🎯 RANDOM STICKER REPLY
        try:
            random_sticker = random.choice(STICKERS)
            await message.reply_sticker(sticker=random_sticker)
        except Exception as stick_err:
            print(f"Sticker reply failed: {stick_err}")

        # Ram memory clear (taki naya character spawn ho sake)
        last_characters.pop(chat_id, None)

        # Success message group me bhejebga
        await message.reply_text(
            f'🌟 <b><a href="tg://user?id={user_id}">{escape(message.from_user.first_name)}</a></b>, you\'ve captured a new character! 🎊\n\n'
            f'<blockquote>📛 <b>𝖭𝖠𝖬𝖤:</b> {grabbed_character["name"]}\n'
            f'🌈 <b>𝖠𝖭𝖨𝖬𝖤:</b> {grabbed_character["anime"]}\n'
            f'✨ <b>𝖱𝖠𝖱𝖨𝖳𝖸:</b> {grabbed_character["rarity"]}\n\n'
            f'💰 <b>𝖤𝖠𝖱𝖭𝖤𝖣:</b> +40 coins 🎉\n'
            f'💳 <b>𝖭𝖤𝖶 𝖡𝖠𝖫𝖠𝖢𝖤:</b> {new_balance} coins</blockquote>',
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await message.reply_text("🕵️‍♂️ ❌ Not quite right! Try again!", parse_mode=enums.ParseMode.HTML)
        
