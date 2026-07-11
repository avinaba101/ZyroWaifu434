# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

import re
import time
from html import escape
from cachetools import TTLCache
from pyrogram import Client, enums
from pyrogram.types import InlineQuery, InlineQueryResultPhoto, InlineQueryResultVideo

from TEAMZYRO import app
from TEAMZYRO.unit.zyro_inline import get_user_collection, search_characters, get_all_characters

# रैम को सुरक्षित रखने के लिए सही कैश लिमिट्स
all_characters_cache = TTLCache(maxsize=2000, ttl=300)
user_collection_cache = TTLCache(maxsize=2000, ttl=30)

@app.on_inline_query()
async def inlinequery(client: Client, inline_query: InlineQuery):
    query = inline_query.query.strip()
    offset = int(inline_query.offset) if inline_query.offset else 0

    user_data = None
    all_characters = []

    # कलेक्शन सर्च हैंडलर
    if query.startswith('collection.'):
        parts = query.split(' ')
        base_query = parts[0].split('.')
        user_id_str = base_query[1]
        search_terms = ' '.join(parts[1:])
        
        if user_id_str.isdigit():
            user_id_int = int(user_id_str)
            user_data = user_collection_cache.get(user_id_int) or await get_user_collection(user_id_int)
            
            if user_data:
                user_collection_cache[user_id_int] = user_data  
                all_characters = list({char['id']: char for char in user_data.get('characters', []) if 'id' in char}.values())
                
                if search_terms:
                    clean_search = search_terms.replace('.AMV', '').strip()
                    if clean_search:
                        regex = re.compile(re.escape(clean_search), re.IGNORECASE)
                        all_characters = [char for char in all_characters if regex.search(char.get('name', '')) or regex.search(char.get('anime', ''))]
    else:
        # नॉर्मल कैरेक्टर सर्च हैंडलर
        if query:
            clean_search = query.replace('.AMV', '').strip()
            if clean_search:
                all_characters = await search_characters(clean_search)
        else:
            all_characters = all_characters_cache.get('all_characters') or await get_all_characters()
            all_characters_cache['all_characters'] = all_characters  

    # AMV (Video) या Photo फ़िल्टर लॉजिक
    if '.AMV' in query:
        all_characters = [char for char in all_characters if 'vid_url' in char]
    else:
        all_characters = [char for char in all_characters if 'img_url' in char]

    # पैजिनेशन (Pagination) - 50 कैरेक्टर्स प्रति पेज
    characters = all_characters[offset:offset + 50]
    next_offset = str(offset + len(characters)) if len(characters) == 50 else ""

    results = []
    for index, character in enumerate(characters):
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

        # आईडी को स्थिर रखा गया है ताकि टेलीग्राम ग्रिड को तुरंत लोड करे
        stable_id = f"{character['id']}_{offset}_{index}"

        if 'vid_url' in character:
            thumbnail_url = character.get('thum_url') or character.get('img_url') or 'https://envs.sh/6Y3.jpg'
            results.append(
                InlineQueryResultVideo(
                    id=stable_id,
                    video_url=character['vid_url'],
                    thumb_url=thumbnail_url,
                    title=" ", # खाली स्पेस ताकि कोई नाम न दिखे
                    mime_type="video/mp4",
                    caption=caption,
                    parse_mode=enums.ParseMode.HTML
                )
            )
        elif 'img_url' in character:
            # 🔥 यहाँ जादू है: title और description को सिर्फ एक खाली स्पेस (" ") दिया गया है
            # इससे टेलीग्राम ग्रिड में कोई भी टेक्स्ट या नाम नहीं दिखाएगा, सिर्फ साफ़ फोटो दिखेगी!
            results.append(
                InlineQueryResultPhoto(
                    id=stable_id,
                    photo_url=character['img_url'],
                    thumb_url=character['img_url'],
                    title=" ",       
                    description=" ", 
                    caption=caption, # फोटो भेजने के बाद नाम और डिटेल्स चैट में दिखेंगी
                    parse_mode=enums.ParseMode.HTML
                )
            )

    try:
        await inline_query.answer(results, next_offset=next_offset, cache_time=5)
    except Exception as e:
        print(f"Inline Query Answer Error: {e}")
        
