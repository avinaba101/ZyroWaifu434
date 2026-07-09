# ==========================================
# Creator: fushiguro
# Bot Name: Anime Catcher
# Remade for Render & VPS Deployment
# Fully Fixed Help Menu & Callbacks by AI
# ==========================================

import os
import importlib.util
import random
import time
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from TEAMZYRO import *
from TEAMZYRO.unit.zyro_help import HELP_DATA  

# 🔹 Function to Calculate Uptime
START_TIME = time.time()

def get_uptime():
    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

# 🔹 Function to Generate Private Start Message & Buttons
async def generate_start_message(client, message):
    bot_user = await client.get_me()
    bot_name = "Anime Catcher"
    ping = round(time.time() - message.date.timestamp(), 2)
    if ping < 0:
        ping = 0
    uptime = get_uptime()
    
    caption = (
        f"🍃 𝖦𝗋𝖾𝖾𝗍𝗂𝗇𝗀𝗌, 𝖨'𝗆 <b>{bot_name}</b> 🫧\n\n"
        f"<blockquote>━━━━━━━▧▣▧━━━━━━━\n"
        f"⦾ <b>𝖶𝖧𝖤𝖱𝖤:</b> 𝖨 𝗌𝗉𝖺𝗐𝗇 𝖺𝗇𝗂𝗆𝖾 𝖼𝗁𝖺𝗋𝖺𝖼𝗍𝖾𝗋𝗌 𝗂𝗇 𝗒𝗈𝗎𝗋 𝖼𝗁𝖺 𝖿𝗈𝗋 𝗎𝗌𝖾𝗋𝗌 𝗍𝗈 𝗀𝗋𝖺𝖻.\n"
        f"⦾ <b>𝖧𝖮𝖶 𝖳𝖮 𝖴𝖲𝖤:</b> 𝖠𝖽𝖽 𝗆𝖾 𝗍𝗈 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉 𝖺𝗇𝖽 𝗎𝗌𝖾 /help 𝖿𝗈𝗋 𝖼command𝗌.\n"
        f"━━━━━━━▧▣▧━━━━━━━\n"
        f"⚡ <b>𝖯𝖨𝖭𝖦:</b> {ping} ms\n"
        f"⏳ <b>𝖴𝖯𝖳𝖨𝖬𝖤:</b> {uptime}</blockquote>"
    )

    buttons = [
        [InlineKeyboardButton("Aᴅᴅ Tᴏ Yᴏᴜʀ Gʀᴏᴜᴘ ", url=f"https://t.me/{bot_user.username}?startgroup=true")],
        [InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url="https://t.me/+hLhjBd4AT3cyNzFl"), 
         InlineKeyboardButton("Cʜᴀɴɴᴇʟ", url="https://t.me/+hLhjBd4AT3cyNzFl")],
        [InlineKeyboardButton("Hᴇʟᴘ", callback_data="open_help")],
        [InlineKeyboardButton("Dᴇᴠᴇʟᴏᴘᴇʀ: ғᴜsʜɪɢᴜʀᴏ", url="https://t.me/darkXmusic")],
    ]
    
    return caption, buttons

# 🔹 Function to Generate Group Start Message & Buttons
async def generate_group_start_message(client):
    bot_user = await client.get_me()
    caption = (
        f"🍃 𝖨'姆 <b>Anime Catcher</b> 🫧\n\n"
        f"<blockquote>𝖨 𝗌𝗉𝖺spawn 𝖺𝗇𝗂𝗆𝖾 𝖼𝗁𝖺𝗋𝖺𝖼𝗍𝖾𝗋𝗌 𝗂𝗇 𝗒𝗈𝗎𝗋 𝗀𝗋𝗈𝗎𝗉 𝗐𝗂𝗍ʜ 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝖼𝗈𝗎นต์𝗌 𝖿𝗈𝗋 𝗉𝗅𝖺𝗒𝖾ʀ𝗌 𝗍𝗈 /guess.\n"
        f"𝖴𝗌𝖾 /help 𝖿ᴏʀ ᴍᴏʀᴇ ɪɴғᴏ.</blockquote>"
    )
    buttons = [
        [
            InlineKeyboardButton("Aᴅᴅ Mᴇ", url=f"https://t.me/{bot_user.username}?startgroup=true"),
            InlineKeyboardButton("Sᴜᴘᴘᴏʀᴛ", url="https://t.me/+hLhjBd4AT3cyNzFl")
        ]
    ]
    return caption, buttons

# 🔹 Send Media (Helper)
async def send_media_message(message, media, caption, buttons):
    if str(media).lower().endswith(('.png', '.jpg', '.jpeg')):
        await message.reply_photo(photo=media, caption=caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    elif str(media).lower().endswith('.gif'):
        await message.reply_animation(animation=media, caption=caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_video(video=media, caption=caption, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

# 🔹 Private Start Command Handler
@app.on_message(filters.command("start") & filters.private)
async def start_private_command(client, message):
    existing_user = await user_collection.find_one({"id": message.from_user.id})
    
    if not existing_user:
        user_data = {
            "id": message.from_user.id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "start_time": time.time()
        }
        await user_collection.insert_one(user_data)

    caption, buttons = await generate_start_message(client, message)
    media = random.choice(START_MEDIA)

    if BOT_LOGGING and str(BOT_LOGGING).strip().lower() != "none":
        try:
            await app.send_message(
                chat_id=int(BOT_LOGGING),
                text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
            )
        except Exception:
            pass

    await send_media_message(message, media, caption, buttons)

# 🔹 Group Start Command Handler
@app.on_message(filters.command("start") & filters.group)
async def start_group_command(client, message):
    caption, buttons = await generate_group_start_message(client)
    media = random.choice(START_MEDIA)
    await send_media_message(message, media, caption, buttons)

# 🔹 /help Command Text Handler (For Direct Commands)
@app.on_message(filters.command("help"))
async def help_command_handler(client, message):
    buttons = find_help_modules()
    if message.chat.type == enums.ChatType.PRIVATE:
        buttons.append([InlineKeyboardButton("⬅ Back", callback_data="back_to_home")])
    
    text = (
        "⚙️ <b>𝖧𝖤𝖫𝖯 𝖬𝖤𝖭𝖴</b>\n\n"
        "<blockquote>ᴄʜᴏᴏsᴇ ᴛʜᴇ ᴄᴀᴛᴇɢᴏʀʏ ғᴏʀ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴɴᴀ ɢᴇᴛ ʜᴇʟᴩ.\n\n"
        "ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ : /</blockquote>"
    )
    
    if message.chat.type == enums.ChatType.PRIVATE:
        media = random.choice(START_MEDIA)
        await send_media_message(message, media, text, buttons)
    else:
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

# 🔹 Function to Find Help Modules
def find_help_modules():
    buttons = []
    for module_name, module_data in HELP_DATA.items():
        button_name = module_data.get("HELP_NAME", "Unknown")
        buttons.append(InlineKeyboardButton(button_name, callback_data=f"help_{module_name}"))
    return [buttons[i : i + 3] for i in range(0, len(buttons), 3)]

# 🔹 Help Button Click Handler
@app.on_callback_query(filters.regex("^open_help$"))
async def show_help_menu(client, query: CallbackQuery):
    buttons = find_help_modules()
    buttons.append([InlineKeyboardButton("⬅ Back", callback_data="back_to_home")])

    text = (
        "⚙️ <b>𝖧𝖤𝖫𝖯 𝖬𝖤𝖭𝖴</b>\n\n"
        "<blockquote>ᴄʜᴏᴏsᴇ ᴛʜᴇ ᴄᴀᴛᴇɢᴏʀʏ ғᴏʀ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴɴᴀ ɢᴇᴛ ʜᴇʟᴩ.\n\n"
        "ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇ दें ᴡɪᴛʜ : /</blockquote>"
    )

    try:
        await query.message.edit_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        try:
            await query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            pass
    await query.answer()

# 🔹 Individual Module Help Handler
@app.on_callback_query(filters.regex(r"^help_(.+)"))
async def show_help(client, query: CallbackQuery):
    module_name = query.data.split("_", 1)[1]
    try:
        module_data = HELP_DATA.get(module_name, {})
        help_text = module_data.get("HELP", "Is module ka koi help nahi hai.")
        buttons = [[InlineKeyboardButton("⬅ Back", callback_data="open_help")]]
        
        full_text = f"<b>{module_name.upper()} Help:</b>\n\n{help_text}"
        
        try:
            await query.message.edit_caption(
                caption=full_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            try:
                await query.message.edit_text(
                    text=full_text,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception:
                pass
    except Exception:
        pass
    await query.answer()

# 🔹 Back to Home
@app.on_callback_query(filters.regex("^back_to_home$"))
async def back_to_home(client, query: CallbackQuery):
    caption, buttons = await generate_start_message(client, query.message)
    try:
        await query.message.edit_caption(
            caption=caption,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        try:
            await query.message.edit_text(
                text=caption,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            pass
    await query.answer()
