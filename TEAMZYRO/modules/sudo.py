# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from TEAMZYRO import OWNER_ID, app, db, require_power

sudo_users = db['sudo_users']

# Predefined powers
ALL_POWERS = ["add", "del", "up", "app", "inv", "VIP"]

# Command: /saddsudo
@app.on_message(filters.command("saddsudo") & filters.reply & filters.group)
@require_power("VIP")
async def add_sudo(client: Client, message: Message):
    replied_user_id = message.reply_to_message.from_user.id

    existing_user = await sudo_users.find_one({"_id": replied_user_id})
    if existing_user:
        await message.reply_text(f"User `{replied_user_id}` is already a sudo.")
        return

    # यहाँ await जोड़ा गया है ताकि डेटाबेस ब्लॉक न हो
    await sudo_users.update_one(
        {"_id": replied_user_id},
        {"$set": {"powers": {"add": True}}},
        upsert=True
    )
    await message.reply_text(f"User `{replied_user_id}` has been added as a sudo with 'add' power.")

# Command: /sremovesudo
@app.on_message(filters.command("sremovesudo"))
@require_power("VIP")
async def remove_sudo(client: Client, message: Message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1 and message.command[1].isdigit():
        user_id = int(message.command[1])
    else:
        await message.reply_text("❌ Please reply to a user or provide a valid user ID.")
        return

    existing_user = await sudo_users.find_one({"_id": user_id})
    if not existing_user:
        await message.reply_text(f"⚠️ User `{user_id}` is not a sudo.")
        return

    await sudo_users.delete_one({"_id": user_id})
    await message.reply_text(f"✅ User [{user_id}](tg://user?id={user_id}) has been removed from sudo.", disable_web_page_preview=True)

# Command: /seditsudo
@app.on_message(filters.command("seditsudo") & filters.reply)
@require_power("VIP")
async def edit_sudo(client: Client, message: Message):
    replied_user_id = message.reply_to_message.from_user.id
    user_data = await sudo_users.find_one({"_id": replied_user_id})

    if not user_data:
        await message.reply_text("This user is not a sudo.")
        return

    buttons = []
    powers = user_data.get("powers", {})
    for power in ALL_POWERS:
        current_status = "Yes" if powers.get(power, False) else "No"
        buttons.append([
            InlineKeyboardButton(f"{power}", callback_data="noop"),
            InlineKeyboardButton(f"{current_status}", callback_data=f"toggle_{replied_user_id}_{power}")
        ])
    
    buttons.append([InlineKeyboardButton("Closed", callback_data="close_keyboard")])
    keyboard = InlineKeyboardMarkup(buttons)
    await message.reply_text(f"Edit powers for `{replied_user_id}`:", reply_markup=keyboard)

# Callback handler for toggling powers
@app.on_callback_query(filters.regex(r"^toggle_(\d+)_(\w+)$"))
async def toggle_power(client: Client, callback_query: CallbackQuery):
    # डेकोरेटर हटाकर अंदर मैनुअल चेक या स्प्लिट डेटा यूज़ किया गया है
    data = callback_query.data.split("_")
    user_id = int(data[1])
    power = data[2]

    # कॉलबैक करने वाले यूज़र की पावर चेक करें
    clicker_data = await sudo_users.find_one({"_id": callback_query.from_user.id})
    if callback_query.from_user.id != OWNER_ID and (not clicker_data or not clicker_data.get("powers", {}).get("VIP", False)):
        await callback_query.answer("You do not have VIP permission to toggle powers!", show_alert=True)
        return

    user_data = await sudo_users.find_one({"_id": user_id})
    if not user_data:
        await callback_query.answer("User not found.", show_alert=True)
        return

    current_status = user_data.get("powers", {}).get(power, False)
    new_status = not current_status
    await sudo_users.update_one(
        {"_id": user_id},
        {"$set": {f"powers.{power}": new_status}}
    )

    await callback_query.answer(f"Power '{power}' updated to {'Yes' if new_status else 'No'}.", show_alert=True)

    user_data = await sudo_users.find_one({"_id": user_id})
    powers = user_data.get("powers", {})
    buttons = []
    for p in ALL_POWERS:
        status = "Yes" if powers.get(p, False) else "No"
        buttons.append([
            InlineKeyboardButton(f"{p}", callback_data="noop"),
            InlineKeyboardButton(f"{status}", callback_data=f"toggle_{user_id}_{p}")
        ])
    
    buttons.append([InlineKeyboardButton("Closed", callback_data="close_keyboard")])
    keyboard = InlineKeyboardMarkup(buttons)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)

# Callback handler for closing the keyboard
@app.on_callback_query(filters.regex(r"^close_keyboard$"))
async def close_keyboard(client: Client, callback_query: CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await callback_query.answer("Keyboard closed.", show_alert=True)

# Command: /sudolist
@app.on_message(filters.command("sudolist"))
async def sudo_list(client: Client, message: Message):
    if message.from_user.id != OWNER_ID:
        await message.reply_text("You do not have permission to use this command.")
        return

    users = await sudo_users.find().to_list(length=None)
    if not users:
        await message.reply_text("There are no sudo users.")
        return

    sudo_list_text = "🛠 **Sudo Users List:**\n\n"
    for user in users:
        user_id = user.get("_id")
        try:
            user_info = await client.get_users(user_id)
            first_name = user_info.first_name
        except:
            first_name = "Unknown"

        sudo_list_text += f"➤ [{first_name}](tg://user?id={user_id}) (`{user_id}`)\n"

    await message.reply_text(sudo_list_text, disable_web_page_preview=True)
