# ==========================================
# Creator: fushiguro
# Remade for: Render & VPS Deployment
# ==========================================

from TEAMZYRO import *
import importlib
import logging
import sys
import TEAMZYRO
from TEAMZYRO.modules import ALL_MODULES
from flask import Flask
import threading
import os

# Render के पोर्ट बाइंडिंग एरर (Port Scan Timeout) से बचने के लिए डमी वेब सर्वर
app = Flask('')

@app.route('/')
def home():
    return "fushiguro Waifu Bot is Running Perfectly!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()


def main() -> None:
    # Render के लिए बैकग्राउंड वेब सर्वर शुरू करें
    keep_alive()
    
    # मॉड्यूल्स लोड करना
    for module_name in ALL_MODULES:
        imported_module = importlib.import_module("TEAMZYRO.modules." + module_name)
    LOGGER("TEAMZYRO.modules").info("𝐀𝐥𝐥 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬 𝐋𝐨𝐚𝐝𝐞𝐝 𝐁𝐚𝐛𝐲🥳...")

    ZYRO.start()

    # FORCE_JOIN एडमिन परमिशन वेरिफिकेशन (FIXED BY AI)
    if FORCE_JOIN and str(FORCE_JOIN).strip() and str(FORCE_JOIN).lower() != "none":
        try:
            try:
                chat_target = int(FORCE_JOIN)
            except ValueError:
                chat_target = FORCE_JOIN
                
            chat_obj = ZYRO.get_chat(chat_target)
            invite_link = chat_obj.invite_link
            if not invite_link:
                invite = ZYRO.create_chat_invite_link(chat_target)
                invite_link = invite.invite_link
                
            TEAMZYRO.FORCE_JOIN_LINK = invite_link
            LOGGER("TEAMZYRO").info(f"Successfully verified FORCE_JOIN admin rights. Link: {invite_link}")
        except Exception as e:
            LOGGER("fushiguro-Log").error(
                "\n"
                "=======================================================================\n"
                "❌ CRITICAL STARTUP ERROR:\n"
                f"Bot is NOT an admin in the FORCE_JOIN channel/chat ({FORCE_JOIN})!\n"
                "======================================================================="
            )
            try:
                ZYRO.stop()
            except:
                pass
            sys.exit(1)
    else:
        LOGGER("TEAMZYRO").info("FORCE_JOIN is empty or None. Skipping force join check... Bot will start normally!")

    # BOT_LOGGING परमिशन वेरिफिकेशन और स्टार्टअप मैसेज
    if BOT_LOGGING and str(BOT_LOGGING).strip() and str(BOT_LOGGING).lower() != "none":
        try:
            try:
                log_target = int(BOT_LOGGING)
            except ValueError:
                log_target = BOT_LOGGING
                
            test_msg = ZYRO.send_message(
                chat_id=log_target,
                text="⚙️ **fushiguro WaifuBot Startup Notification**:\nSuccessfully connected & verified write permissions in the logs channel!"
            )
            LOGGER("TEAMZYRO").info(f"Successfully verified BOT_LOGGING permissions. Test message sent (ID: {test_msg.id}).")
        except Exception as e:
            LOGGER("fushiguro-Log").error(
                "\n"
                "=======================================================================\n"
                "❌ CRITICAL STARTUP ERROR:\n"
                f"Bot cannot post/send messages to BOT_LOGGING chat ({BOT_LOGGING})!\n"
                "======================================================================="
            )
            try:
                ZYRO.stop()
            except:
                pass
            sys.exit(1)
    else:
        LOGGER("TEAMZYRO").info("BOT_LOGGING is empty. Skipping log channel verification...")

    # स्टार्टअप लोगो और मैसेज (यह बॉट पोलिंग शुरू होने से पहले दिखेगा)
    LOGGER("TEAMZYRO").info(
        "\n╔════════════════════════╗\n"
        "  ☠︎︎ MADE BY FUSHIGURO ☠︎︎\n"
        "╚════════════════════════╝"
    )
    
    try:
        send_start_message()
    except Exception:
        pass

    # बॉट को चालू (Live) रखना और मैसेजेस सुनना (FIXED BY AI)
    from pyrogram import idle
    idle()
    try:
        ZYRO.stop()
    except:
        pass
    

if __name__ == "__main__":
    main()
    
