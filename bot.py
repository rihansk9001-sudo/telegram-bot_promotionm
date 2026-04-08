import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatJoinRequest
import random
import string
from flask import Flask
import threading
import os
import time
import re
import json

# Aapki Details
TOKEN = "8350483074:AAEgbf-GWrDTW5BNk6CS22-97ZtRfMivpjU" 
ADMIN_ID = 1484173564

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================== PERMANENT DATABASE SETUP ================== #
DB_FILE = "database.json"

CHANNELS = {} 
GEN_LINKS = {} 
USER_STATES = {} 
TEMP_BULK_CHANNELS = {} 
USER_REQUESTS = {} 

def load_data():
    global CHANNELS, GEN_LINKS, USER_REQUESTS
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                CHANNELS = {int(k): v for k, v in data.get("channels", {}).items()}
                GEN_LINKS = data.get("links", {})
                USER_REQUESTS = {int(k): [int(cid) for cid in v] for k, v in data.get("requests", {}).items()}
        except Exception as e:
            print("Database load error:", e)

def save_data():
    with open(DB_FILE, "w") as f:
        json.dump({"channels": CHANNELS, "links": GEN_LINKS, "requests": USER_REQUESTS}, f)

load_data()

# ============================================================= #

VIDEO_URL = "https://files.catbox.moe/4hbu2q.mp4"
CAPTION_TEMPLATE = """💎 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 {name} 
 𝗧𝗢 ZX 𝗠𝗢𝗗𝗦 𝗗𝗥𝗜𝗣 𝗞𝗘𝗬 

🎮 𝗬𝗼𝘂𝗿 𝗙𝗥𝗘𝗘 𝗙𝗜𝗥𝗘 𝗔𝗣𝗞𝗠𝗢𝗗 𝗞𝗘𝗬 𝗶𝘀 𝗷𝘂𝘀𝘁 𝗼𝗻𝗲 𝘀𝘁𝗲𝗽 𝗮𝘄𝗮𝘆! 🔥
━━━━━━━━━━━━━━━

🛠️ 𝗠𝗢𝗗 𝗙𝗘𝗔𝗧𝗨𝗥𝗘𝗦:
✅ 𝗦𝗶𝗹𝗲𝗻𝘁 𝗞𝗶𝗹𝗹 / 𝗦𝗶𝗹𝗲 𝗮𝗻𝘁𝗶-Tat𝘂
✅ 𝗠𝗮𝗴𝗻𝗲𝘁𝗶𝗰 𝗔𝗶𝗺
✅ 𝗔𝗻𝘁𝗶-𝗧𝗮𝘁𝘂 / Speed Hack
✅ 𝗚𝗵𝗼𝘀𝘁 𝗛𝗮𝗰𝗸 / 𝗦𝗽𝗲𝗲𝗱 𝗛𝗮𝗰𝗸
✅ 𝗘𝗦𝗣 (𝗡𝗮𝗺𝗲, 𝗟𝗶𝗻𝗲, 𝗕𝗼𝘅)

━━━━━━━━━━━━━━━
🚨 𝗔𝗖𝗖𝗘𝗦𝗦 𝗚𝗘𝗧 𝗞𝗔𝗥𝗡𝗘 𝗞𝗘 𝗟𝗜𝗬𝗘

📢 𝗡𝗶𝗰𝗵𝗲 𝗱𝗶𝘆𝗲 𝗴𝗮𝘆𝗲 𝘀𝗮𝗿𝗲 𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀 𝗝𝗢𝗜𝗡 𝗸𝗮𝗿𝗻𝗮 𝗭𝗔𝗥𝗨𝗥𝗜 𝗵𝗮𝗶
━━━━━━━━━━━━━━━
1️⃣ 𝗦𝗮𝗯𝗵𝗶 𝗰𝗵𝗮𝗻𝗻𝗲𝗹𝘀 𝗝𝗼𝗶𝗻 𝗸𝗮𝗿𝗲𝗶𝗻
2️⃣ 𝗝𝗼𝗶𝗻 𝗸𝗲 𝗯𝗮𝗮𝗱 "♻️ Try Again" 𝗯𝘂𝘁𝘁𝗼𝗻 𝗽𝗮𝗿 𝗰𝗹𝗶𝗰𝗸 𝗸𝗮𝗿𝗲𝗶𝗻
━━━━━━━━━━━━━━━"""

# ================== BOSS ADMIN PANEL ================== #

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("➕ Bulk Add Channels", callback_data="panel_bulk_add", style="success"),
        InlineKeyboardButton("➖ Remove Channel", callback_data="panel_rem", style="danger")
    )
    markup.row(
        InlineKeyboardButton("📋 View Channels", callback_data="panel_view", style="primary"),
        InlineKeyboardButton("📊 Stats", callback_data="panel_stats", style="primary")
    )
    markup.row(
        InlineKeyboardButton("📢 Broadcast", callback_data="panel_broad", style="primary"),
        InlineKeyboardButton("🚫 Ban User", callback_data="panel_ban", style="danger")
    )
    
    bot.reply_to(message, "🧑‍💻 **Boss Admin Panel**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('panel_'))
def handle_admin_panel(call):
    if call.from_user.id != ADMIN_ID: return
    action = call.data.split('_', 1)[1]
    
    if action == "bulk_add":
        msg = bot.send_message(call.message.chat.id, "Kripya apne saare **Channel IDs** bhejein (Space ya nayi line dekar alag karein).\n\n*Example:*\n`-100123456789 -100987654321`", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_bulk_channel_ids)
        
    elif action == "rem":
        if not CHANNELS:
            bot.answer_callback_query(call.id, "Koi channel add nahi hai!", show_alert=True)
            return
        markup = InlineKeyboardMarkup()
        for ch_id, data in CHANNELS.items():
            markup.add(InlineKeyboardButton(f"❌ Remove {data['name']}", callback_data=f"del_{ch_id}", style="danger"))
        bot.send_message(call.message.chat.id, "Kis channel ko remove karna hai?", reply_markup=markup)
        
    elif action == "view":
        if not CHANNELS:
            bot.send_message(call.message.chat.id, "List khali hai.")
            return
        text = "📋 **Added Channels:**\n\n"
        for ch_id, data in CHANNELS.items():
            text += f"ID: `{ch_id}` | Color: {data['color']} | Name: {data['name']}\n"
        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")
        
    elif action == "stats":
        bot.send_message(call.message.chat.id, "📊 **Bot Stats:**\n\nTotal Channels: {}\nTotal Links Generated: {}".format(len(CHANNELS), len(GEN_LINKS)))
        
    elif action == "broad":
        bot.send_message(call.message.chat.id, "📊 **Broadcast logic:**\n\nAbhi database connected nahi hai isliye real broadcast available nahi hai.")
        
    elif action == "ban":
        bot.send_message(call.message.chat.id, "🚫 **Ban User:**\n\nAbhi ban feature active nahi hai.")
        
    bot.answer_callback_query(call.id)

# --- BULK ADD LOGIC ---
def process_bulk_channel_ids(message):
    if message.from_user.id != ADMIN_ID: return
    
    raw_text = message.text
    ids = re.split(r'[\s\n,]+', raw_text.strip())
    
    success_channels = {}
    failed_ids = []
    
    bot.reply_to(message, "⏳ Checking Admin Rights & Generating Join Request Links...")
    
    for cid in ids:
        if not cid: continue
        try:
            ch_id = int(cid)
            member = bot.get_chat_member(ch_id, bot.user.id)
            if member.status in ['administrator', 'creator']:
                chat = bot.get_chat(ch_id)
                
                try:
                    invite = bot.create_chat_invite_link(ch_id, creates_join_request=True)
                    link = invite.invite_link
                except Exception as e:
                    link = bot.export_chat_invite_link(ch_id)
                    
                success_channels[ch_id] = {"url": link, "name": chat.title}
            else:
                failed_ids.append(cid)
        except Exception:
            failed_ids.append(cid)
            
    response_text = ""
    
    if failed_ids:
        response_text += "❌ **Bot in channels me Admin NAHI hai ya ID galat hai:**\n" + "\n".join(failed_ids) + "\n\n"
        
    if success_channels:
        response_text += "✅ **Ye channels successfully Check ho gaye:**\n"
        for ch_id, data in success_channels.items():
            response_text += f"- {data['name']}\n"
            
        response_text += "\n🎨 **Ab in naye channels ke liye Button Color select karein:**"
        
        global TEMP_BULK_CHANNELS
        TEMP_BULK_CHANNELS = success_channels
        
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("🔵 Primary (Blue)", callback_data="bulkcolor_primary", style="primary"),
            InlineKeyboardButton("🟢 Success (Green)", callback_data="bulkcolor_success", style="success"),
            InlineKeyboardButton("🔴 Danger (Red)", callback_data="bulkcolor_danger", style="danger")
        )
        bot.send_message(message.chat.id, response_text, reply_markup=markup, parse_mode="Markdown")
    else:
        if not failed_ids:
            bot.send_message(message.chat.id, "Koi valid ID nahi mili.")
        else:
            bot.send_message(message.chat.id, response_text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith('bulkcolor_'))
def save_bulk_color(call):
    if call.from_user.id != ADMIN_ID: return
    color_style = call.data.split('_')[1]
    
    global TEMP_BULK_CHANNELS
    count = 0
    for ch_id, data in TEMP_BULK_CHANNELS.items():
        CHANNELS[ch_id] = {
            "url": data['url'],
            "name": data['name'],
            "color": color_style
        }
        count += 1
        
    TEMP_BULK_CHANNELS = {} 
    save_data() 
    bot.edit_message_text(f"✅ **Done!** {count} Channels successfully `{color_style}` color ke sath add ho gaye hain.", call.message.chat.id, call.message.message_id, parse_mode="Markdown")

# --- REMOVE CHANNEL LOGIC ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('del_'))
def delete_channel(call):
    if call.from_user.id != ADMIN_ID: return
    ch_id = int(call.data.split('_')[1])
    if ch_id in CHANNELS:
        del CHANNELS[ch_id]
        save_data() 
        bot.edit_message_text("✅ Channel successfully removed!", call.message.chat.id, call.message.message_id)

# ================== GETLINK FUNCTION ================== #

@bot.message_handler(commands=['getlink'])
def getlink_cmd(message):
    if message.from_user.id != ADMIN_ID: return
    msg = bot.reply_to(message, "Send A Message For To Get Your Shareable Link 🔇")
    bot.register_next_step_handler(msg, process_genlink)

def process_genlink(message):
    proc_msg = bot.reply_to(message, "processing...")
    time.sleep(1)
    
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    GEN_LINKS[code] = {"message_id": message.message_id, "chat_id": message.chat.id}
    save_data() 
    
    bot_info = bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={code}"
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("↗️ SHARE URL", url=f"https://t.me/share/url?url={link}", style="success"))
    
    bot.delete_message(message.chat.id, proc_msg.message_id)
    bot.reply_to(message, f"Here is your link:\n\n{link}", reply_markup=markup, disable_web_page_preview=True)

# ================== JOIN REQUEST TRACKER ================== #
@bot.chat_join_request_handler()
def handle_join_request(request: ChatJoinRequest):
    user_id = request.from_user.id
    ch_id = request.chat.id
    
    if user_id not in USER_REQUESTS:
        USER_REQUESTS[user_id] = []
        
    if ch_id not in USER_REQUESTS[user_id]:
        USER_REQUESTS[user_id].append(ch_id)
        save_data() 

# ================== USER FLOW ================== #

def check_user_joined(user_id):
    not_joined = []
    for ch_id in CHANNELS:
        if user_id in USER_REQUESTS and ch_id in USER_REQUESTS[user_id]:
            continue 

        try:
            status = bot.get_chat_member(ch_id, user_id).status
            if status not in ['member', 'administrator', 'creator']:
                not_joined.append(ch_id)
        except:
            not_joined.append(ch_id)
    return not_joined

def get_sub_keyboard(not_joined_channels):
    markup = InlineKeyboardMarkup()
    
    # 🔥 FIX: Hamesha EXACTLY 2-2 ki grid banegi (Chahe 3 ho ya 4 buttons)
    # Jo channel join nahi kiya gaya hai, bas WAHI screen pe dikhega
    buttons = []
    for ch_id in not_joined_channels:
        data = CHANNELS[ch_id]
        buttons.append(InlineKeyboardButton(text=f"Join {data['name']}", url=data['url'], style=data['color']))
    
    # Grid logic (do-do buttons ek row me dalega)
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.row(buttons[i], buttons[i+1])
        else:
            markup.row(buttons[i])
            
    markup.add(InlineKeyboardButton("♻️ Try Again", callback_data="check_join", style="success"))
    return markup

@bot.message_handler(commands=['start'])
def start_cmd(message):
    payload = message.text.replace('/start', '').strip()
    if payload:
        USER_STATES[message.from_user.id] = payload

    caption = CAPTION_TEMPLATE.format(name=message.from_user.first_name)
    not_joined = check_user_joined(message.from_user.id)
    
    # Agar user ne pehle se hi sab kuch join kiya hua hai
    if len(not_joined) == 0:
        send_hidden_file(message.from_user.id, message.chat.id)
        return

    # User ko video aur SIRF BAAKI bache hue buttons dikhao (2x2 grid me)
    bot.send_video(message.chat.id, video=VIDEO_URL, caption=caption, reply_markup=get_sub_keyboard(not_joined))

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def verify_join(call):
    user_id = call.from_user.id
    not_joined = check_user_joined(user_id)
    
    if len(not_joined) > 0:
        bot.answer_callback_query(call.id, "❌ Aapne abhi tak saare channels join/request nahi kiye hain!", show_alert=True)
        # 🔥 VIDEO JAISA EFFECT: Ab button wahi rahenge jo join/request karne baaki hain
        try:
            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=get_sub_keyboard(not_joined)
            )
        except Exception:
            pass 
    else:
        bot.answer_callback_query(call.id, "✅ Verification Successful!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_hidden_file(user_id, call.message.chat.id)

def send_hidden_file(user_id, chat_id):
    if user_id in USER_STATES:
        code = USER_STATES[user_id]
        if code in GEN_LINKS:
            data = GEN_LINKS[code]
            bot.copy_message(chat_id=chat_id, from_chat_id=data['chat_id'], message_id=data['message_id'])
        del USER_STATES[user_id]
    else:
        bot.send_message(chat_id, "🎉 **Access Granted!** Aap verified hain.")

# ================== FLASK SETUP ================== #
@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_bot():
    try:
        bot.remove_webhook()
        time.sleep(1)
        print("🤖 Bot Started Super Fast...")
        bot.infinity_polling(skip_pending=True, allowed_updates=['message', 'callback_query', 'chat_join_request'])
    except Exception as e:
        print(f"❌ ERROR AAYA: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
