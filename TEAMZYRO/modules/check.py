# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

# TEAMZYRO/commands/check.py
from TEAMZYRO import app, collection as character_collection, user_collection
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import asyncio 

@app.on_message(filters.command("check"))
async def check_character(client, message):
    args = message.command
    if len(args) < 2:
        await message.reply_text("Please provide a Character ID: `/check <character_id>`")
        return

    character_id = args[1]
    character = await character_collection.find_one({'id': character_id})

    if not character:
        await message.reply_text("Character not found.")
        return

    # Create the 'Who Have It' button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Who Have It", callback_data=f"whohaveit_{character_id}")]
    ])

    # 🔥 FIX 1: Character Info text ko proper blockquote gherav ke andar kiya
    text = (
        f"🌟 <b>𝖢𝖧𝖠𝖱𝖠𝖢𝖳𝖤𝖱 𝖨𝖭𝖥𝖮</b>\n\n"
        f"<blockquote>🆔 <b>𝖨𝖣:</b> <code>{character_id}</code>\n"
        f"📛 <b>𝖭𝖠𝖬𝖤:</b> {character['name']}\n"
        f"📺 <b>𝖠𝖭𝖨𝖬𝖤:</b> {character['anime']}\n"
        f"💎 <b>𝖱𝖠𝖱𝖨𝖳𝖸:</b> {character['rarity']}</blockquote>"
    )

    if 'vid_url' in character:
        await message.reply_video(character['vid_url'], caption=text, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_photo(character['img_url'], caption=text, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML)


@app.on_callback_query(filters.regex("^whohaveit_"))
async def who_have_it(client, callback_query):
    character_id = callback_query.data.split("_")[1]

    # Find users who own the character
    users = await user_collection.find({'characters.id': character_id}).to_list(length=10)

    if not users:
        await callback_query.answer("No one owns this character yet!", show_alert=True)
        return

    # 🔥 FIX 2: Owners list ke numbers aur names ko clean kiya aur use bhi blockquote box me daala
    owner_text = "🏆 <b>𝖳𝖮𝖯 𝖮𝖶𝖭𝖤𝖱𝖲 𝖫𝖨𝖲𝖳</b>\n\n<blockquote>"
    for i, user in enumerate(users, 1):
        user_name = user.get('first_name', 'Unknown')
        count = sum(1 for char in user.get("characters", []) if char["id"] == character_id)
        owner_text += f"{i}. <a href='tg://user?id={user['id']}'>{user_name}</a> — x{count}\n"
    owner_text += "</blockquote>"

    # Edit message to include the owner list and remove the button
    await callback_query.message.edit_caption(
        caption=f"{callback_query.message.caption}\n\n{owner_text}",
        reply_markup=None,
        parse_mode=enums.ParseMode.HTML
    )
    
