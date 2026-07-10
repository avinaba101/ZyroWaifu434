# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

import re
from cachetools import TTLCache
from TEAMZYRO import user_collection, collection

# कैश को ऑप्टिमाइज़ किया गया ताकि मेमोरी ओवरफ्लो न हो
all_characters_cache = TTLCache(maxsize=2000, ttl=300)  
user_collection_cache = TTLCache(maxsize=5000, ttl=30)  

async def get_user_collection(user_id):
    """Get user collection from database with consistent typing"""
    try:
        # कंसिस्टेंट इंटीजर टाइप का उपयोग करें ताकि की-मैपिंग एरर न हो
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        return None
        
    if user_id_int in user_collection_cache:
        return user_collection_cache[user_id_int]
    
    user = await user_collection.find_one({'id': user_id_int})
    if user:
        user_collection_cache[user_id_int] = user
    return user

async def search_characters(query, force_refresh=False):
    """Search characters based on name or anime with memory limit"""
    if not query:
        return []
        
    cache_key = f"search_{query.lower().strip()}"
    if not force_refresh and cache_key in all_characters_cache:
        return all_characters_cache[cache_key]
    
    # regex एस्केपिंग ताकि स्पेशल कैरेक्टर्स से बोट क्रैश न हो
    safe_query = re.escape(query.strip())
    regex = re.compile(safe_query, re.IGNORECASE)
    
    # length=None की जगह 100 की लिमिट लगाई गई है ताकि रैम फ्रीज न हो
    characters = await collection.find({"$or": [
        {"name": regex},
        {"anime": regex},
        {"aliases": regex}
    ]}).to_list(length=100)
    
    all_characters_cache[cache_key] = characters
    return characters

async def get_all_characters(force_refresh=False):
    """Get all characters with safety batch limit"""
    if not force_refresh and 'all_characters' in all_characters_cache:
        return all_characters_cache['all_characters']
    
    # सुरक्षित लिमिट (मैक्सिमम 1000 कैरेक्टर्स एक बार में लोड होंगे)
    characters = await collection.find({}).to_list(length=1000)
    all_characters_cache['all_characters'] = characters
    return characters

async def refresh_character_caches():
    """Force refresh all caches safely"""
    all_characters_cache.clear()
    user_collection_cache.clear()
