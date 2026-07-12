# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from cachetools import TTLCache

from TEAMZYRO import (app, group_user_totals_collection, locks, 
                      user_cooldowns, last_user, warned_users, 
                      send_image)

# Data load kam karne ke liye cache
group_ctime_cache = TTLCache(maxsize=1000, ttl=60)

# ⏱️ PERFECT FIX: 4 minutes drop interval (4 minutes * 60 seconds = 240 seconds)
SPAWN_TIME_LIMIT = 240  
last_spawn_time = {}

# 🛠️ group=-100 par set hai taaki baaki koi command block na ho
@app.on_message(filters.group & filters.text, group=-100)
async def message_counter(client: Client, message: Message):
    try:
        # 🚀 Agar koi command ya bot game chal raha ho, toh bina roke aage jaane do
        if message.text and message.text.strip().startswith("/"):
            message.continue_propagation()
            return

        if not message.from_user:
            message.continue_propagation()
            return

        chat_id = message.chat.id
        user_id = message.from_user.id
        current_time = time.time()

        # 1. Lock Mechanism for Safety
        if chat_id not in locks:
            locks[chat_id] = asyncio.Lock()
        lock = locks[chat_id]

        async with lock:
            # 2. Strict Spam Control Logic (15-Min Block Penalty)
            if user_id in user_cooldowns:
                if current_time < user_cooldowns[user_id]:
                    # Agar user already block hai, toh message ignore karke return kar jao
                    message.continue_propagation()
                    return
                else:
                    user_cooldowns.pop(user_id, None)

            # Check agar wahi same user lagatar message bhej kar spam kar raha hai
            if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
                last_user[chat_id]['count'] += 1
                
                # Agar 10 messages lagatar spam kiye bina break ke
                if last_user[chat_id]['count'] >= 10:
                    # 900 seconds = Pure 15 Minutes ka strict spam block penalty
                    if user_id not in warned_users or current_time - warned_users[user_id] >= 900:
                        user_cooldowns[user_id] = current_time + 900
                        warned_users[user_id] = current_time
                        try:
                            await message.reply_text(
                                f"⚠️ Don't Spam {message.from_user.first_name}...\n"
                                "Your Messages Will be ignored for 15 Minutes..."
                            )
                        except Exception:
                            pass
                    message.continue_propagation()
                    return
            else:
                last_user[chat_id] = {'user_id': user_id, 'count': 1}

            # 3. ⏱️ Time-based Drop Logic (Har 4 Mins Me Drop)
            if chat_id not in last_spawn_time:
                last_spawn_time[chat_id] = current_time

            # Check kya pichle character drop se lekar ab tak 4 minutes (240s) beet chuke hain?
            if current_time - last_spawn_time[chat_id] >= SPAWN_TIME_LIMIT:
                last_spawn_time[chat_id] = current_time  # Timer reset karo
                try:
                    await send_image(client, message)
                except Exception as e:
                    print(f"Spawn Error in Group {chat_id}: {e}")

    except Exception as main_err:
        print(f"Handler Error: {main_err}")
    
    # Baaki features ko normal run hone dene ke liye propagation continue rakhein
    message.continue_propagation()
  
