# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

import os
import random
import html

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from TEAMZYRO import (app, PHOTO_URL, OWNER_ID,
                      user_collection, top_global_groups_collection, 
                      group_user_totals_collection)


# Global Leaderboard Command
@app.on_message(filters.command("TopGroups"))
async def global_leaderboard(client: Client, message: Message):
    cursor = top_global_groups_collection.aggregate([
        {"$project": {"group_name": 1, "count": 1}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    leaderboard_message = "<b>TOP 10 GROUPS WHO GUESSED MOST CHARACTERS</b>\n\n"

    for i, group in enumerate(leaderboard_data, start=1):
        group_name = html.escape(group.get('group_name', 'Unknown'))

        if len(group_name) > 15:
            group_name = group_name[:15] + '...'
        count = group['count']
        leaderboard_message += f'{i}. <b>{group_name}</b> ➾ <b>{count}</b>\n'

    photo_url = random.choice(PHOTO_URL)
    await message.reply_photo(photo=photo_url, caption=leaderboard_message, parse_mode=enums.ParseMode.HTML)


# Group Top Users Command
@app.on_message(filters.command("ctop") & filters.group)
async def ctop(client: Client, message: Message):
    chat_id = message.chat.id

    # यहाँ बग को ठीक किया गया है: chat_id को str() में बदला गया है ताकि MongoDB से सही मैच हो सके
    cursor = group_user_totals_collection.aggregate([
        {"$match": {"group_id": str(chat_id)}},
        {"$project": {"username": 1, "first_name": 1, "character_count": "$count"}},
        {"$sort": {"character_count": -1}},
        {"$limit": 10}
    ])
    leaderboard_data = await cursor.to_list(length=10)

    if not leaderboard_data:
        await message.reply_text("<b>⚠️ No stats found for this group yet!</b>", parse_mode=enums.ParseMode.HTML)
        return

    leaderboard_message = "<b>TOP 10 USERS WHO GUESSED CHARACTERS MOST TIME IN THIS GROUP..</b>\n\n"

    for i, user in enumerate(leaderboard_data, start=1):
        username = user.get('username')
        first_name = html.escape(user.get('first_name', 'Unknown'))

        if len(first_name) > 15:
            first_name = first_name[:15] + '...'
        character_count = user['character_count']
        
        if username:
            leaderboard_message += f'{i}. <a href="https://t.me/{username}"><b>{first_name}</b></a> ➾ <b>{character_count}</b>\n'
        else:
            leaderboard_message += f'{i}. <b>{first_name}</b> ➾ <b>{character_count}</b>\n'

    photo_url = random.choice(PHOTO_URL)
    await message.reply_photo(photo=photo_url, caption=leaderboard_message, parse_mode=enums.ParseMode.HTML)


# Stats Command
@app.on_message(filters.command("st"))
async def stats(client: Client, message: Message):
    user_count = await user_collection.count_documents({})
    group_count = await group_user_totals_collection.distinct('group_id')

    await message.reply_text(f'Total Users: {user_count}\nTotal groups: {len(group_count)}')
  
