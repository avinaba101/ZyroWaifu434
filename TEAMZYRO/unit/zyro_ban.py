# ==========================================
# Creator: MrZyro
# Telegram: @MrZyro_dev
# GitHub: https://github.com/MrZyro
# ==========================================

import time
from TEAMZYRO import user_cooldowns

async def check_cooldown(user_id: int) -> bool:
    current_time = time.time()
    if user_id in user_cooldowns:
        cooldown_end = user_cooldowns[user_id]
        if current_time < cooldown_end:
            return True
        else:
            # मेमोरी को साफ़ रखने के लिए पुराना कूलडाउन हटा दें
            user_cooldowns.pop(user_id, None)
    return False

async def get_remaining_cooldown(user_id: int) -> int:
    current_time = time.time()
    if user_id in user_cooldowns:
        cooldown_end = user_cooldowns[user_id]
        if current_time < cooldown_end:
            return max(1, int(cooldown_end - current_time))
        else:
            user_cooldowns.pop(user_id, None)
    return 0
