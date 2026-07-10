# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

from functools import wraps
from pyrogram import Client
from pyrogram.types import CallbackQuery, Message
# TEAMZYRO से जरूरी वेरिएबल्स को साफ तरीके से इम्पोर्ट करना
from TEAMZYRO import db, OWNER_ID

# यहाँ अपनी या को-ओनर की टेलीग्राम ID डालें (जैसे: 12345678)
CO_OWNER_ID = 0

sudo_users = db['sudo_users']

# Predefined powers
ALL_POWERS = ["add", "del", "up", "app", "inv", "VIP"]

def require_power(required_power):
    def decorator(func):
        @wraps(func)
        async def wrapper(client: Client, update, *args, **kwargs):
            # यह चेक करेगा कि इवेंट कॉलबैक क्वेरी है या नॉर्मल मैसेज
            if isinstance(update, CallbackQuery):
                user_id = update.from_user.id
                
                # ओनर या को-ओनर चेक बायपास
                if user_id == OWNER_ID or user_id == CO_OWNER_ID:
                    return await func(client, update, *args, **kwargs)

                user_data = await sudo_users.find_one({"_id": user_id})
                if not user_data or not user_data.get("powers", {}).get(required_power, False):
                    await update.answer(
                        f"You do not have the '{required_power}' power required to use this button.", 
                        show_alert=True
                    )
                    return
                return await func(client, update, *args, **kwargs)

            elif isinstance(update, Message):
                user_id = update.from_user.id if update.from_user else None
                if not user_id:
                    return

                # ओनर या को-ओनर चेक बायपास
                if user_id == OWNER_ID or user_id == CO_OWNER_ID:
                    return await func(client, update, *args, **kwargs)

                user_data = await sudo_users.find_one({"_id": user_id})
                if not user_data or not user_data.get("powers", {}).get(required_power, False):
                    await update.reply_text(
                        f"⚠️ You do not have the '{required_power}' power required to use this command."
                    )
                    return
                return await func(client, update, *args, **kwargs)
                
            return await func(client, update, *args, **kwargs)
        return wrapper
    return decorator

async def is_vip_or_owner(user_id: int) -> bool:
    if user_id == OWNER_ID or user_id == CO_OWNER_ID:
        return True
    user_data = await sudo_users.find_one({"_id": user_id})
    if user_data and user_data.get("powers", {}).get("VIP", False):
        return True
    return False
