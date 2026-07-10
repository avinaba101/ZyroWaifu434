# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

import re
import time
from html import escape
from cachetools import TTLCache
from pyrogram import Client, filters, enums
from pyrogram.types import InlineQuery, InlineQueryResultPhoto, InlineQueryResultVideo

from TEAMZYRO import app # Pyrogram क्लाइंट (बोट ऑब्जेक्ट)
from TEAMZYRO.unit.zyro_inline import * # आपके पुराने फंक्शन्स (get_user_collection, search_characters आदि)

all_characters_cache = TTLCache(maxsize=10000, ttl=36000)  # Cache for all characters
user_collection_cache = TTLCache(maxsize=10000, ttl=60)  # Cache for user collections

@app.on_inline_query()
async def inlinequery(client: Client, inline_query: InlineQuery):
    query = inline_query.query
    offset = int(inline_query.offset) if inline_query.offset else 0

    user_data = None
    all_characters = []

    # Check if query is for a user's collection
    if query.startswith('collection.'):
        parts = query.split(' ')
        base_query = parts[0].split('.')
        user_id = base_query[1]
        search_terms = ' '.join(parts[1:])
        
        if user_id.isdigit():
            user_data = user_collection_cache.get(user_id) or await get_user_collection(user_id)
            if user_data:
                user_collection_cache[user_id] = user_data  # Cache the result
                # Deduplicate by ID
                all_characters = list({char['id']: char for char in user_data.get('characters', []) if 'id' in char}.values())
                
                if search_terms:
                    # AMV फ़िल्टर शब्द को सर्च टर्म्स में से हटा रहे हैं ताकि सर्च सही हो
                    clean_search = search_terms.replace('.AMV', '').strip()
                    if clean_search:
                        regex = re.compile(clean_search, re.IGNORECASE)
                        all_characters = [char for char in all_characters if regex.search(char.get('name', '')) or regex.search(char.get('anime', ''))]
    else:
        # General character search
        if query:
            clean_search = query.replace('.AMV', '').strip()
            if clean_search:
                all_characters = await search_characters(clean_search)
        else:
            all_characters = all_characters_cache.get('all_characters') or await get_all_characters()
            all_characters_cache['all_characters'] = all_characters  # Cache the result

    # Filter characters based on whether they have a video or image
    if '.AMV' in query:
        all_characters = [char for char in all_characters if 'vid_url' in char]
    else:
        all_characters = [char for char in all_characters if 'img_url' in char]

    # Pagination logic
    characters = all_characters[offset:offset + 50]
    next_offset = str(offset + len(characters)) if len(characters) == 50 else ""

    # Construct results for inline query
    results = []
    for character in characters:
        # Generate caption safely
        if user_data:
            user_character_count = sum(1 for char in user_data.get('characters', []) if 'id' in char and char['id'] == character['id'])
            caption = (
                f"<b>👤 Check out <a href='tg://user?id={user_data['id']}'>{escape(user_data.get('first_name', 'User'))}</a>'s character:</b>\n\n"
                f"🌸 <b>{character['name']} (x{user_character_count})</b>\n"
                f"🏖️ From: <b>{character['anime']}</b>\n"
                f"🔮 Rarity: <b>{character['rarity']}</b>\n\n"
                f"🆔️ <b>{character['id']}</b>\n\n"
            )
        else:
            caption = (
                f"<b>Discover this amazing character:</b>\n\n"
                f"🌸 <b>{character['name']}</b>\n"
                f"🏖️ From: <b>{character['anime']}</b>\n"
                f"🔮 Rarity: <b>{character['rarity']}</b>\n"
                f"🆔️ <b>{character['id']}</b>\n\n"
            )

        unique_id = f"{character['id']}_{int(time.time())}_{offset}"

        # If the character has a video URL, create a video result
        if 'vid_url' in character:
            thumbnail_url = character.get('thum_url') or character.get('img_url') or 'https://envs.sh/6Y3.jpg'
            results.append(
                InlineQueryResultVideo(
                    video_url=character['vid_url'],
                    thumb_url=thumbnail_url,
                    title=character['name'],
                    mime_type="video/mp4",
                    description=f"From: {character['anime']} | Rarity: {character['rarity']}",
                    caption=caption,
                    parse_mode=enums.ParseMode.HTML
                )
            )
        elif 'img_url' in character:
            # Add photo result to inline query results
            results.append(
                InlineQueryResultPhoto(
                    photo_url=character['img_url'],
                    thumb_url=character['img_url'],
                    caption=caption,
                    parse_mode=enums.ParseMode.HTML
                )
            )

    # Send the results with pagination
    await inline_query.answer(results, next_offset=next_offset, cache_time=5)
