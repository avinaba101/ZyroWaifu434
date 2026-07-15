# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

import time
from pyrogram import Client, filters
from pyrogram.types import Message

from TEAMZYRO import app, is_vip_or_owner

@app.on_message(filters.command("ping"))
async def ping(client: Client, message: Message):
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return
        
    if not await is_vip_or_owner(user_id):
        await message.reply_text("noo nigga🌚 this is for my boss🫡 you can go and play ludo😋..")
        return
        
    start_time = time.time()
    reply_msg = await message.reply_text('pinging🇵🇹🍃!')
    end_time = time.time()
    
    elapsed_time = round((end_time - start_time) * 1000, 3)
    await reply_msg.edit_text(f'Yelo Boss🫡 Pong🍃🇵🇹! {elapsed_time}ms')
