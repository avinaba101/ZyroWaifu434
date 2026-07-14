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

# 🎭 RANDOM STICKERS LIST (Working Telegram Standard Stickers)
STICKERS = [
    "CAACAgIAAxkBAAEl4nFmR...", 
    "CAACAgIAAxkBAAEl4nNmR...", 
    "CAACAgIAAxkBAAEl4nVmR...", 
    "CAACAgIAAxkBAAEl4ndmR..."
]

@app.on_message(filters.command(["guess", "protecc", "collect", "grab", "hunt"]) & filters.group)
async def guess(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None
    
    if not user_id:
        return
        
    current_time = time.time()
    today = datetime.now(timezone.utc).date()

    # 1. COOLDOWN SECURITY CHECK
    if user_id in guess_cooldowns:
        time_passed = current_time - guess_cooldowns[user_id]
        if time_passed < GUESS_COOLDOWN_TIME:
            remaining = int(GUESS_COOLDOWN_TIME - time_passed)
            try:
                await message.reply_text(f"⚠️ Slow down! Wait {remaining}s.")
            except:
                pass
            return

    # Global cooling verification
    if await check_cooldown(user_id):
        remaining_time = await get_remaining_cooldown(user_id)
        await message.reply_text(f"⚠️ Cooldown active. Wait {remaining_time}s.")
        return

    # Session validity check
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
    
    # 2. MATCHING LOGIC ENGINE
    if sorted(name_parts) == sorted(guess_word.split()) or any(part == guess_word for part in name_parts):
        first_correct_guesses[chat_id] = user_id
        
        # Expire session task ko cancel karna
        for task in asyncio.all_tasks():
            if task.get_name() == f"expire_session_{chat_id}":
                task.cancel()
                break

        grabbed_character = last_characters[chat_id]

        # ⏳ SPEED / TIME TAKEN CALCULATION LOGIC
        # Agar spawn file me timestamp save ho raha hai toh yeh exact seconds nikalega
        spawn_timestamp = grabbed_character.get('timestamp')
        if spawn_timestamp:
            elapsed_time = time.time() - spawn_timestamp
            # Agar 1 second se kam laga toh decimal me dikhayega warna round figure me seconds dikhayega
            time_taken_str = f"{elapsed_time:.1f}s" if elapsed_time < 1 else f"{int(elapsed_time)}s"
        else:
            time_taken_str = "Fast!" # Fallback agar main spawn file me timestamp missing ho

        # 3. 💾 DATABASE COMMIT (100% SAFE - DATA DELETE NAHI HOGA)
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
                '$push': {'characters': grabbed_character} 
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

        # 4. 🎯 STICKER DISPATCH SYSTEM (Guess Message Par Sticker Reply)
        try:
            chosen_sticker = random.choice(STICKERS)
            await message.reply_sticker(sticker=chosen_sticker)
        except Exception as sticker_error:
            print(f"Sticker bypass: {sticker_error}")

        # 5. 🗑️ AUTO DEEP-SCAN GROUP CLEANUP LOGIC
        try:
            # User ke guess wale text ko turant delete karega
            await message.delete()
            
            # Deep scan loop group ki purani spawn photo nikal kar delete karne ke liye
            async for history_msg in client.get_chat_history(chat_id, limit=100):
                if history_msg.from_user and history_msg.from_user.id == client.me.id:
                    if history_msg.photo or history_msg.document:
                        await history_msg.delete() 
                        break
        except Exception as cleanup_error:
            print(f"Group cleanup bypassed: {cleanup_error}")

        # Memory clean taaki agla spawn normal ho sake
        last_characters.pop(chat_id, None)

        # Success message text send karega group me (Jisme ab TIME TAKEN bhi print hoga)
        await client.send_message(
            chat_id=chat_id,
            text=f'🌟 <b><a href="tg://user?id={user_id}">{escape(message.from_user.first_name)}</a></b>, you\'ve captured a new character! 🎊\n\n'
                 f'<blockquote>📛 <b>𝖭𝖠𝖬𝖤:</b> {grabbed_character["name"]}\n'
                 f'🌈 <b>𝖠𝖭𝖨𝖬𝖤:</b> {grabbed_character["anime"]}\n'
                 f'✨ <b>𝖱𝖠𝖱𝖨𝖳𝖸:</b> {grabbed_character["rarity"]}\n\n'
                 f'⏱️ <b>𝖳𝖨𝖬𝖤 𝖳𝖠𝖪𝖤𝖭:</b> {time_taken_str}\n' # 👈 Yeh line speed aur dynamic time show karegi
                 f'💰 <b>𝖤𝖠𝖱𝖭𝖤𝖣:</b> +40 coins 🎉\n'
                 f'💳 <b>𝖭𝖤𝖶 𝖡𝖠𝖫𝖠𝖢𝖤:</b> {new_balance} coins</blockquote>',
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await message.reply_text("🕵️‍♂️ ❌ Not quite right! Try again!", parse_mode=enums.ParseMode.HTML)
        
