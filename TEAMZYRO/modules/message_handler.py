# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

from TEAMZYRO import *
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters, ContextTypes
import asyncio
import time

async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id
    current_time = time.time()

    # Fetch or initialize group data - Changed default ctime from 80 to 5
    existing_group = await group_user_totals_collection.find_one({"group_id": chat_id})
    if not existing_group:
        await group_user_totals_collection.update_one(
            {"group_id": chat_id}, 
            {"$set": {"group_id": chat_id, "ctime": 5}},  # <--- यहाँ 5 मैसेजेस सेट कर दिए हैं
            upsert=True
        )
        ctime = 5
    else:
        ctime = existing_group.get("ctime", 5)  # <--- यहाँ भी डिफ़ॉल्ट 5 कर दिया है

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
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
                    cooldown_end = current_time + 600  # 10 minutes se block
                    user_cooldowns[user_id] = cooldown_end
                    warned_users[user_id] = current_time
                    await update.message.reply_text(
                        f"⚠️ Don't Spam {update.effective_user.first_name}...\n"
                        "Your Messages Will be ignored for 10 Minutes..."
                    )
                return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        # Normal chats ke liye ctime messages par ek character bhejna hai
        if chat_id in normal_message_counts:
            normal_message_counts[chat_id] += 1
        else:
            normal_message_counts[chat_id] = 1

        if normal_message_counts[chat_id] % ctime == 0:
            await send_image(update, context)
            normal_message_counts[chat_id] = 0  # Reset count

application.add_handler(MessageHandler(~filters.COMMAND, message_counter, block=False))
