# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import Message

# TEAMZYRO से आपके जरूरी कलेक्टर्स, लॉक और सेंड_इमेज फ़ंक्शन इम्पोर्ट हो रहे हैं
from TEAMZYRO import (app, group_user_totals_collection, locks, 
                      user_cooldowns, last_user, warned_users, 
                      normal_message_counts, send_image)

@app.on_message(filters.group & ~filters.command)
async def message_counter(client: Client, message: Message):
    chat_id = str(message.chat.id)
    user_id = message.from_user.id if message.from_user else None
    current_time = time.time()

    if not user_id:
        return

    # Fetch or initialize group data
    existing_group = await group_user_totals_collection.find_one({"group_id": chat_id})
    if not existing_group:
        await group_user_totals_collection.update_one(
            {"group_id": chat_id}, 
            {"$set": {"group_id": chat_id, "ctime": 5}},  # डिफ़ॉल्ट 5 मैसेजेस सेट हैं
            upsert=True
        )
        ctime = 5
    else:
        ctime = existing_group.get("ctime", 5)

    # Lock का लॉजिक ताकि डेटा आपस में न टकराए
    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        # एंटी-स्पैम और कूलडाउन चेक
        if user_id in user_cooldowns:
            cooldown_end = user_cooldowns[user_id]
            if current_time < cooldown_end:
                return
            else:
                del user_cooldowns[user_id]

        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
                if user_id not in warned_users or current_time - warned_users[user_id] >= 600:
                    cooldown_end = current_time + 600  # 10 मिनट के लिए ब्लॉक
                    user_cooldowns[user_id] = cooldown_end
                    warned_users[user_id] = current_time
                    await message.reply_text(
                        f"⚠️ Don't Spam {message.from_user.first_name}...\n"
                        "Your Messages Will be ignored for 10 Minutes..."
                    )
                return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        # ग्रुप के मैसेजेस की गिनती बढ़ाना
        if chat_id in normal_message_counts:
            normal_message_counts[chat_id] += 1
        else:
            normal_message_counts[chat_id] = 1

        # अगर गिनती ctime (जैसे 5 या 10) के बराबर हो जाए, तो कैरेक्टर स्पॉन करो
        if normal_message_counts[chat_id] % ctime == 0:
            # ध्यान दें: आपका send_image फ़ंक्शन Pyrogram के हिसाब से (client, message) लेता है या नहीं, यह सुनिश्चित कर लें
            await send_image(client, message)
            normal_message_counts[chat_id] = 0  # काउंट रीसेट करें
