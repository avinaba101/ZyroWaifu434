# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

from TEAMZYRO import *
from html import escape
import asyncio
import time
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from datetime import datetime, timezone

# react.py se react_to_message function ko import kiya gaya hai
from TEAMZYRO.modules.react import react_to_message 

# ⏱️ COMMAND SPAM CONTROL: Per user cooldown tracking in memory
GUESS_COOLDOWN_TIME = 8  
guess_cooldowns = {}

@app.on_message(filters.command(["guess", "protecc", "collect", "grab", "hunt"]) & filters.group)
async def guess(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None
    
    if not user_id:
        return
        
    current_time = time.time()
    today = datetime.now(timezone.utc).date()

    # EXTRA STRICT COOLDOWN CHECK
    if user_id in guess_cooldowns:
        time_passed = current_time - guess_cooldowns[user_id]
        if time_passed < GUESS_COOLDOWN_TIME:
            remaining = int(GUESS_COOLDOWN_TIME - time_passed)
            try:
                await message.reply_text(f"⚠️ Slow down! Wait {remaining}s before guessing again.")
            except:
                pass
            return

    # Global cooling check
    if await check_cooldown(user_id):
        remaining_time = await get_remaining_cooldown(user_id)
        await message.reply_text(
            f"⚠️ You are still in cooldown. Please wait {remaining_time} seconds before using any commands."
        )
        return

    # सेशन वैलिडिटी चेक (Auto-remove ke baad ye block trigger hoga agar koi dubara guess karega)
    if chat_id not in last_characters or 'name' not in last_characters.get(chat_id, {}):
        await message.reply_text("❌ Character Guess not available for this chat.")
        return

    if chat_id in first_correct_guesses:
        await message.reply_text("❌ This character has already been guessed!")
        return

    if last_characters[chat_id].get('ranaway', False):
        await message.reply_text("❌ THE CHARACTER HAS ALREADY RUN AWAY!")
        return 

    guess_word = ' '.join(message.command[1:]).lower().strip() if len(message.command) > 1 else ''
    
    if not guess_word:
        await message.reply_text("Please provide a character name after the command.")
        return

    if "()" in guess_word or "&" in guess_word:
        await message.reply_text("Nahh You Can't use These Types of words in your guess..❌️")
        return

    # Set timestamp immediately
    guess_cooldowns[user_id] = current_time

    name_parts = last_characters[chat_id]['name'].lower().split()
    
    # Name matching logic
    if sorted(name_parts) == sorted(guess_word.split()) or any(part == guess_word for part in name_parts):
        first_correct_guesses[chat_id] = user_id
        
        # Purana timer cancel karna
        for task in asyncio.all_tasks():
            if task.get_name() == f"expire_session_{chat_id}":
                task.cancel()
                break

        timestamp = last_characters[chat_id].get('timestamp')
        if timestamp:
            time_taken = time.time() - timestamp
            time_taken_str = f"{int(time_taken)} seconds"
        else:
            time_taken_str = "Unknown time"

        if user_id not in user_guess_progress or user_guess_progress[user_id]["date"] != today:
            user_guess_progress[user_id] = {"date": today, "count": 0}

        user_guess_progress[user_id]["count"] += 1
        
        # Grabbed character data target variable me copy karna delete karne se pehle
        grabbed_character = last_characters[chat_id]

        # DB Update logic
        user_data = await user_collection.find_one({'id': user_id})
        if user_data:
            new_balance = user_data.get('balance', 0) + 40
            await user_collection.update_one(
                {'id': user_id},
                {
                    '$set': {
                        'username': message.from_user.username,
                        'first_name': message.from_user.first_name,
                        'balance': new_balance
                    },
                    '$push': {'characters': grabbed_character}
                }
            )
        else:
            new_balance = 40
            await user_collection.insert_one({
                'id': user_id,
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'characters': [grabbed_character],
                'balance': new_balance
            })

        group_name = message.chat.title or f"Group_{chat_id}"
        await top_global_groups_collection.update_one(
            {'group_id': str(chat_id)},
            {
                '$set': {'group_name': group_name},
                '$inc': {'count': 1}
            },
            upsert=True
        )

        # 🔥 FEATURE 1 FIX: Sahi guess hote hi memory se waifu data automatic delete/remove
        last_characters.pop(chat_id, None)

        try:
            await react_to_message(chat_id, message.id)
        except Exception as e:
            print(f"Reaction Error: {e}")

        # Success message
        await message.reply_text(
            f'🌟 <b><a href="tg://user?id={user_id}">{escape(message.from_user.first_name)}</a></b>, you\'ve captured a new character! 🎊\n\n'
            f'<blockquote>📛 <b>𝖭𝖠𝖬𝖤:</b> {grabbed_character["name"]}\n'
            f'🌈 <b>𝖠𝖭𝖨𝖬𝖤:</b> {grabbed_character["anime"]}\n'
            f'✨ <b>𝖱𝖠𝖱𝖨𝖳𝖸:</b> {grabbed_character["rarity"]}\n\n'
            f'⏱️ <b>𝖳𝖨𝖬𝖤 𝖳𝖠𝖪𝖤𝖭:</b> {time_taken_str}\n'
            f'💰 <b>𝖤𝖠𝖱𝖤𝖭𝖣:</b> +40 coins 🎉\n'
            f'💳 <b>𝖭𝖤𝖶 𝖡𝖠𝖫𝖠𝖭𝖢𝖤:</b> {new_balance} coins\n\n'
            f'This Character has been added to Your Harem. Use /harem to see your harem.</blockquote>',
            parse_mode=enums.ParseMode.HTML
        )
    else:
        incorrect_text = (
            "🕵️‍♂️ <b>𝖦𝖴𝖤𝖲𝖲 𝖥𝖠𝖨𝖫𝖤𝖣</b>\n\n"
            "<blockquote>❌ Not quite right, brave guesser! Try again and unveil the mystery character!</blockquote>"
        )
        await message.reply_text(
            incorrect_text,
            parse_mode=enums.ParseMode.HTML
        )
        
