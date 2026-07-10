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
                      normal_message_counts, send_image)

# डेटाबेस लोड कम करने के लिए ग्रुप लिमिट का छोटा कैश
group_ctime_cache = TTLCache(maxsize=1000, ttl=60)

# 💡 स्पॉन लिमिट को बढ़ाकर बिल्कुल परफेक्ट 20 मैसेज कर दिया गया है
DEFAULT_SPAWN_LIMIT = 20 

@app.on_message(filters.group & ~filters.command)
async def message_counter(client: Client, message: Message):
    if not message.from_user:
        return

    chat_id = message.chat.id
    chat_id_str = str(chat_id)
    user_id = message.from_user.id
    current_time = time.time()

    # 1. ग्रुप की स्पॉन लिमिट (ctime) निकालना
    if chat_id in group_ctime_cache:
        ctime = group_ctime_cache[chat_id]
    else:
        existing_group = await group_user_totals_collection.find_one({"group_id": chat_id_str})
        if not existing_group:
            await group_user_totals_collection.update_one(
                {"group_id": chat_id_str}, 
                {"$set": {"group_id": chat_id_str, "ctime": DEFAULT_SPAWN_LIMIT}}, 
                upsert=True
            )
            ctime = DEFAULT_SPAWN_LIMIT
        else:
            ctime = existing_group.get("ctime", DEFAULT_SPAWN_LIMIT)
        group_ctime_cache[chat_id] = ctime

    # 2. लॉक मैकेनिज्म (Concurrency Safety)
    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        # 3. एंटी-स्पैम और कूलडाउन चेक
        if user_id in user_cooldowns:
            if current_time < user_cooldowns[user_id]:
                return
            else:
                user_cooldowns.pop(user_id, None)

        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
                if user_id not in warned_users or current_time - warned_users[user_id] >= 600:
                    user_cooldowns[user_id] = current_time + 600
                    warned_users[user_id] = current_time
                    try:
                        await message.reply_text(
                            f"⚠️ Don't Spam {message.from_user.first_name}...\n"
                            "Your Messages Will be ignored for 10 Minutes..."
                        )
                    except Exception:
                        pass
                return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        # 4. मैसेज काउंटिंग लॉजिक
        normal_message_counts[chat_id] = normal_message_counts.get(chat_id, 0) + 1

        # 5. कैरेक्टर स्पॉन ट्रिगर (अब पूरे 20 मैसेज होने पर ही चलेगा)
        if normal_message_counts[chat_id] >= ctime:
            normal_message_counts[chat_id] = 0 # पहले काउंट रीसेट करें
            try:
                # हमारा फिक्स किया हुआ Pyrogram आधारित send_image रन होगा
                await send_image(client, message)
            except Exception as e:
                print(f"Spawn Error in Group {chat_id}: {e}")
              
