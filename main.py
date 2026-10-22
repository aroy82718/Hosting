# -*- coding: utf-8 -*-
import telebot
from telebot import types
import subprocess
import os
import zipfile
import tempfile
import shutil
import time
import psutil
import json
import threading
import re
import uuid 
import sys
import atexit
import signal
import html
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread    

# ==================== CUSTOM BUTTON CLASSES ====================
class CustomKeyboardButton(types.KeyboardButton):
    def __init__(self, text, style=None, icon_custom_emoji_id=None, **kwargs):
        super().__init__(text, **kwargs)
        self.style = style
        self.icon_custom_emoji_id = icon_custom_emoji_id

    def to_dict(self):
        d = super().to_dict()
        if self.style:
            d['style'] = self.style
        if self.icon_custom_emoji_id:
            d['icon_custom_emoji_id'] = str(self.icon_custom_emoji_id)
        return d

class CustomInlineKeyboardButton(types.InlineKeyboardButton):
    def __init__(self, text, style=None, icon_custom_emoji_id=None, **kwargs):
        super().__init__(text, **kwargs)
        self.style = style
        self.icon_custom_emoji_id = icon_custom_emoji_id

    def to_dict(self):
        d = super().to_dict()
        if self.style:
            d['style'] = self.style
        if self.icon_custom_emoji_id:
            d['icon_custom_emoji_id'] = str(self.icon_custom_emoji_id)
        return d

# ==================== CUSTOM EMOJI TAGS ====================
CE_CROWN = '<tg-emoji emoji-id="5769547529993588669">👑</tg-emoji>'
CE_DIAMOND = '<tg-emoji emoji-id="5767137507879685567">💎</tg-emoji>'
CE_LIGHTNING = '<tg-emoji emoji-id="5987803826512466184">⚡</tg-emoji>'
CE_CHECK = '<tg-emoji emoji-id="6030437742066798869">✅</tg-emoji>'
CE_CROSS = '<tg-emoji emoji-id="6030331836763213973">❌</tg-emoji>'
CE_SPARKLE = '<tg-emoji emoji-id="5987715818337603766">✨</tg-emoji>'
CE_STAR = '<tg-emoji emoji-id="6032819460346220361">⭐</tg-emoji>'
CE_STOP = '<tg-emoji emoji-id="6267262260243076354">🛑</tg-emoji>'
CE_PLAY = '<tg-emoji emoji-id="6266829404849050968">▶️</tg-emoji>'
CE_LOCK = '<tg-emoji emoji-id="6282846669335702032">🔒</tg-emoji>'
CE_UNLOCK = '<tg-emoji emoji-id="6028551194861899805">🛡</tg-emoji>'
CE_BELL = '<tg-emoji emoji-id="6264510702329797113">🔔</tg-emoji>'
CE_BROADCAST = '<tg-emoji emoji-id="5780405967527089720">📢</tg-emoji>'
CE_PACKAGE = '<tg-emoji emoji-id="6269214795325510848">📦</tg-emoji>'
CE_GREEN = '<tg-emoji emoji-id="6028220478085140634">🟢</tg-emoji>'
CE_RED = '<tg-emoji emoji-id="6030331836763213973">🔴</tg-emoji>'
CE_ID = '<tg-emoji emoji-id="6035239240625820254">🆔</tg-emoji>'
CE_TIMER = '<tg-emoji emoji-id="6267229004311303657">⌛</tg-emoji>'
CE_STATS = '<tg-emoji emoji-id="6033118016407868078">📊</tg-emoji>'
CE_MAIL = '<tg-emoji emoji-id="6264777724741556322">✉️</tg-emoji>'
CE_HELP = '<tg-emoji emoji-id="6282525354242348869">❓</tg-emoji>'
CE_ROCKET = '<tg-emoji emoji-id="5780773956030043338">🚀</tg-emoji>'
CE_PIN = '<tg-emoji emoji-id="6267172559851099903">📌</tg-emoji>'
CE_WARN = '<tg-emoji emoji-id="6267039884016358504">⚠️</tg-emoji>'
CE_SKULL = '<tg-emoji emoji-id="6035142758480482309">💀</tg-emoji>'
CE_GLOBE = '<tg-emoji emoji-id="6028126693179264852">🌐</tg-emoji>'

# ==================== CONFIG ====================
TOKEN = '8849202188:AAFOycWuJ1wypyYWBK9crDhx2m4QQZbOGTI'
OWNER_ID = 6914205738
ADMIN_IDS = {6914205738}

CHANNELS_FILE = 'force_channels.json'
USERS_DATA_FILE = 'users_db.json'
PLANS_FILE = 'plans_file.json'
REDEEM_CODES_FILE = 'redeem_codes.json'
BANNED_USERS_FILE = 'banned_users.json'
SETTINGS_FILE = 'bot_settings.json'

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    default_settings = {
        "upi_id": "merchant@upi",
        "upload_channel": -1004362983175  # Default upload channel/group ID
    }
    save_settings(default_settings)
    return default_settings

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

BOT_SETTINGS = load_settings()

def load_force_channels():
    if os.path.exists(CHANNELS_FILE):
        try:
            with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    default_channels = [
        {"id": "@AADITYAXFF", "name": "Main Channel"},
        {"id": "@BOTSBYAADITYA", "name": "Main Group"}
    ]
    save_force_channels(default_channels)
    return default_channels

def save_force_channels(channels):
    try:
        with open(CHANNELS_FILE, 'w', encoding='utf-8') as f:
            json.dump(channels, f, indent=4)
    except Exception as e:
        print(f"Error saving force channels: {e}")

FORCE_CHANNELS = load_force_channels()

# ==================== DATABASE & MANAGEMENT ====================
def load_db():
    if os.path.exists(USERS_DATA_FILE):
        try:
            with open(USERS_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_db(data):
    try:
        with open(USERS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving users db: {e}")

def load_plans():
    if os.path.exists(PLANS_FILE):
        try:
            with open(PLANS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    default_plans = [
        {"id": "day_pack", "name": "1 Day Pack", "price": "₹20 / $0.25", "days": 1},
        {"id": "week_pack", "name": "7 Days Pack", "price": "₹100 / $1.20", "days": 7},
        {"id": "month_pack", "name": "30 Days Pack", "price": "₹300 / $3.50", "days": 30}
    ]
    save_plans(default_plans)
    return default_plans

def save_plans(plans):
    try:
        with open(PLANS_FILE, 'w', encoding='utf-8') as f:
            json.dump(plans, f, indent=4)
    except Exception as e:
        print(f"Error saving plans: {e}")

def load_redeem_codes():
    if os.path.exists(REDEEM_CODES_FILE):
        try:
            with open(REDEEM_CODES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_redeem_codes(codes):
    try:
        with open(REDEEM_CODES_FILE, 'w', encoding='utf-8') as f:
            json.dump(codes, f, indent=4)
    except Exception as e:
        print(f"Error saving redeem codes: {e}")

def load_banned_users():
    if os.path.exists(BANNED_USERS_FILE):
        try:
            with open(BANNED_USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_banned_users(banned_list):
    try:
        with open(BANNED_USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(banned_list, f, indent=4)
    except Exception as e:
        print(f"Error saving banned users: {e}")

USERS_DB = load_db()
PLANS = load_plans()
REDEEM_CODES = load_redeem_codes()
BANNED_USERS = load_banned_users()

def is_user_banned(user_id):
    return user_id in BANNED_USERS or str(user_id) in [str(x) for x in BANNED_USERS]

def is_user_premium(user_id):
    str_uid = str(user_id)
    if str_uid in USERS_DB:
        expiry = USERS_DB[str_uid].get("premium_expiry")
        if expiry:
            try:
                exp_date = datetime.fromisoformat(expiry)
                if datetime.now() < exp_date:
                    return True
                else:
                    USERS_DB[str_uid]["premium_expiry"] = None
                    save_db(USERS_DB)
            except:
                pass
    return False

# ==================== SETUP ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'user_scripts')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def cleanup_orphaned_processes():
    for root, dirs, files in os.walk(UPLOAD_DIR):
        for file in files:
            if file.endswith('.pid'):
                pid_path = os.path.join(root, file)
                try:
                    with open(pid_path, 'r') as f:
                        pid = int(f.read().strip())
                    try:
                        parent = psutil.Process(pid)
                        children = parent.children(recursive=True)
                        for child in children:
                            child.kill()
                        parent.kill()
                    except psutil.NoSuchProcess:
                        pass
                except Exception:
                    pass
                finally:
                    if os.path.exists(pid_path):
                        try: os.remove(pid_path)
                        except: pass

cleanup_orphaned_processes()

running_scripts = {}
bot_locked = False
user_temp_data = {}
pending_files = {}
screenshot_waiting = {}
reject_waiting = {}
admin_temp_state = {}

bot = telebot.TeleBot(TOKEN, parse_mode=None)

# ==================== FLASK KEEP ALIVE ====================
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ==================== SAFE FUNCTIONS ====================
def safe_send(chat_id, text, reply_markup=None, parse_mode='HTML'):
    try:
        return bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        print(f"Send error: {e}")
        return None

def safe_edit(chat_id, msg_id, text, reply_markup=None, parse_mode='HTML'):
    try:
        return bot.edit_message_text(text, chat_id, msg_id, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        print(f"Edit error: {e}")
        return None

def safe_callback(call_id, text=None, show_alert=False):
    try:
        if text:
            bot.answer_callback_query(call_id, text, show_alert=show_alert)
        else:
            bot.answer_callback_query(call_id)
    except:
        pass

MENU_COMMANDS = [
    'UPLOAD FILE', 'MY SCRIPTS', 'INSTALL MODULE', 'STATS', 
    'BOT SPEED', 'HELP', 'BUY PREMIUM', 'REDEEM CODE', 'SETTINGS & ADMIN', 'ADMIN PANEL', 'MY PROFILE'
]

def route_menu_command(message):
    text = message.text.strip() if message.text else ""
    if text == 'UPLOAD FILE': upload_prompt(message)
    elif text == 'MY SCRIPTS': list_scripts(message)
    elif text == 'INSTALL MODULE': install_module_prompt(message)
    elif text == 'STATS': show_stats(message)
    elif text == 'BOT SPEED': bot_speed(message)
    elif text == 'HELP': show_help(message)
    elif text == 'MY PROFILE': my_profile(message)
    elif text == 'BUY PREMIUM': show_buy_premium(message)
    elif text == 'REDEEM CODE': redeem_code_prompt(message)
    elif text in ['SETTINGS & ADMIN', 'ADMIN PANEL']: admin_panel(message)
    elif text.startswith('/start'): send_welcome(message)

def is_cancel_command(message):
    if not message.text:
        return False
    text = message.text.strip()
    if text.lower() == '/cancel' or text in MENU_COMMANDS or text.startswith('/start'):
        return True
    return False

# ==================== HELPER FUNCTIONS ====================
def get_user_dir(user_id):
    user_dir = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def get_user_scripts(user_id):
    user_dir = get_user_dir(user_id)
    scripts = []
    for f in os.listdir(user_dir):
        if f.endswith(('.py', '.js')):
            scripts.append(f)
    return scripts

def get_user_files_count(user_id):
    user_dir = get_user_dir(user_id)
    count = 0
    for root, dirs, files in os.walk(user_dir):
        count += len([f for f in files if not f.endswith('.log')])
    return count

def get_all_users():
    users = []
    for d in os.listdir(UPLOAD_DIR):
        if os.path.isdir(os.path.join(UPLOAD_DIR, d)) and d.isdigit():
            users.append(int(d))
    return users

def get_total_files_system():
    count = 0
    for root, dirs, files in os.walk(UPLOAD_DIR):
        count += len([f for f in files if not f.endswith('.log')])
    return count

def is_script_running(user_id, script_name):
    key = f"{user_id}_{script_name}"
    if key in running_scripts:
        proc = running_scripts[key].get('process')
        if proc and proc.poll() is None:
            return True
        else:
            del running_scripts[key]
    return False

def stop_script(user_id, script_name):
    key = f"{user_id}_{script_name}"
    user_dir = get_user_dir(user_id)
    pid_path = os.path.join(user_dir, f"{script_name}.pid")
    
    if key in running_scripts:
        proc = running_scripts[key].get('process')
        if proc:
            try:
                parent = psutil.Process(proc.pid)
                children = parent.children(recursive=True)
                for child in children:
                    child.terminate()
                parent.terminate()
                time.sleep(1)
                for child in children:
                    if child.is_running():
                        child.kill()
                if parent.is_running():
                    parent.kill()
            except:
                pass
        del running_scripts[key]
        if os.path.exists(pid_path):
            try: os.remove(pid_path)
            except: pass
        return True
    return False

def delete_user_script(user_id, script_name):
    user_dir = get_user_dir(user_id)
    script_path = os.path.join(user_dir, script_name)
    log_path = script_path.replace('.py', '.log').replace('.js', '.log')
    
    stop_script(user_id, script_name)
    
    deleted = []
    if os.path.exists(script_path):
        os.remove(script_path)
        deleted.append(script_name)
    if os.path.exists(log_path):
        os.remove(log_path)
    return deleted

def validate_script(script_path):
    if script_path.endswith('.py'):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, script_path, 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
    return True, None

def install_package(module_name, chat_id):
    try:
        msg = safe_send(chat_id, f"{CE_PACKAGE} Installing <code>{module_name}</code>...")
        if not msg: return False
        
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', module_name], capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            safe_edit(chat_id, msg.message_id, f"{CE_CHECK} Successfully installed: <code>{module_name}</code>")
            return True
        else:
            safe_edit(chat_id, msg.message_id, f"{CE_CROSS} Failed to install: <code>{module_name}</code>")
            return False
    except Exception as e:
        safe_send(chat_id, f"{CE_CROSS} Error: {str(e)}")
        return False

def is_user_joined(user_id):
    global FORCE_CHANNELS
    if not FORCE_CHANNELS:
        return True
    try:
        for ch in FORCE_CHANNELS:
            chat_id = ch['id']
            try:
                chat_member = bot.get_chat_member(chat_id, user_id)
                if chat_member.status not in ['member', 'administrator', 'creator']:
                    return False
            except:
                return False
        return True
    except:
        return False

# ==================== SUB-SERVICES ====================
BACKUP_DATA_FILES = [CHANNELS_FILE, USERS_DATA_FILE, PLANS_FILE, REDEEM_CODES_FILE, BANNED_USERS_FILE, SETTINGS_FILE]

def create_full_backup():
    """Zip of all user scripts + all json data files. Layout: data/<file>.json , user_scripts/<uid>/..."""
    zip_path = os.path.join(tempfile.gettempdir(), f"server_backup_{int(time.time())}.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for fname in BACKUP_DATA_FILES:
            if os.path.exists(fname):
                zipf.write(fname, f"data/{fname}")
        for root, _, files in os.walk(UPLOAD_DIR):
            for file in files:
                if file.endswith('.pid'):
                    continue
                file_path = os.path.join(root, file)
                arcname = "user_scripts/" + os.path.relpath(file_path, UPLOAD_DIR).replace(os.sep, '/')
                try:
                    zipf.write(file_path, arcname)
                except Exception:
                    pass
        zipf.writestr("backup_info.json", json.dumps({"created": datetime.now().isoformat(), "format": 2}))
    return zip_path

def send_backup_to(chat_id, caption):
    zip_path = None
    try:
        zip_path = create_full_backup()
        size_mb = os.path.getsize(zip_path) / (1024 * 1024)
        if size_mb > 49:
            safe_send(chat_id, f"{CE_CROSS} Backup too large for Telegram ({size_mb:.1f} MB, limit 50 MB).")
            return False
        with open(zip_path, 'rb') as f:
            bot.send_document(chat_id, f, caption=caption, visible_file_name=os.path.basename(zip_path))
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        safe_send(chat_id, f"{CE_CROSS} Backup failed: {html.escape(str(e))}")
        return False
    finally:
        if zip_path and os.path.exists(zip_path):
            try: os.remove(zip_path)
            except: pass

def backup_task():
    while True:
        time.sleep(2 * 3600)
        try:
            send_backup_to(OWNER_ID, "Automated 2-Hour Server Backup (scripts + users data). Restore it from Admin Panel > RESTORE.")
        except Exception as e:
            print(f"Backup task failed: {e}")

# ==================== SCRIPT RUNNERS ====================
def kill_previous_instances(user_dir, script_name):
    for p in psutil.process_iter(['pid', 'cmdline', 'cwd']):
        try:
            cmd = p.info.get('cmdline')
            cwd = p.info.get('cwd')
            if cmd and cwd:
                if any(script_name in c for c in cmd) and cwd == user_dir:
                    try:
                        parent = psutil.Process(p.pid)
                        for child in parent.children(recursive=True):
                            child.kill()
                        parent.kill()
                    except:
                        pass
        except:
            pass

def run_python_script(script_path, user_id, script_name, chat_id):
    key = f"{user_id}_{script_name}"
    user_dir = get_user_dir(user_id)
    log_path = script_path.replace('.py', '.log')
    pid_path = f"{script_path}.pid"
    
    try:
        kill_previous_instances(user_dir, script_name)
        log_file = open(log_path, 'w', encoding='utf-8')
        process = subprocess.Popen(
            [sys.executable, "-u", script_path], cwd=user_dir, stdout=log_file, stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        with open(pid_path, 'w') as f:
            f.write(str(process.pid))
            
        running_scripts[key] = {'process': process, 'log_path': log_path, 'start_time': datetime.now(), 'log_file': log_file}
        safe_send(chat_id, f"{CE_CHECK} Script <code>{script_name}</code> started successfully!")
        
        def monitor():
            process.wait()
            log_file.close()
            if os.path.exists(pid_path):
                try: os.remove(pid_path)
                except: pass
            if key in running_scripts:
                del running_scripts[key]
                exit_code = process.returncode
                status = "successfully" if exit_code == 0 else f"with error (Code: {exit_code})"
                msg = f"{CE_STOP} Script <code>{script_name}</code> stopped {status}."
                
                if exit_code != 0:
                    try:
                        with open(log_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            if lines:
                                last_lines = "".join(lines[-10:])
                                msg += f"\n\n<b>Last log output:</b>\n<pre>{html.escape(last_lines)}</pre>"
                    except:
                        pass
                
                safe_send(chat_id, msg)
        threading.Thread(target=monitor, daemon=True).start()
    except Exception as e:
        safe_send(chat_id, f"{CE_CROSS} Error: {str(e)}")

def run_js_script(script_path, user_id, script_name, chat_id):
    key = f"{user_id}_{script_name}"
    user_dir = get_user_dir(user_id)
    log_path = script_path.replace('.js', '.log')
    pid_path = f"{script_path}.pid"
    
    try:
        kill_previous_instances(user_dir, script_name)
        log_file = open(log_path, 'w', encoding='utf-8')
        process = subprocess.Popen(
            ['node', script_path], cwd=user_dir, stdout=log_file, stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
        
        with open(pid_path, 'w') as f:
            f.write(str(process.pid))
            
        running_scripts[key] = {'process': process, 'log_path': log_path, 'start_time': datetime.now(), 'log_file': log_file}
        safe_send(chat_id, f"{CE_CHECK} JavaScript Script <code>{script_name}</code> started!")
        
        def monitor():
            process.wait()
            log_file.close()
            if os.path.exists(pid_path):
                try: os.remove(pid_path)
                except: pass
            if key in running_scripts:
                del running_scripts[key]
                exit_code = process.returncode
                status = "successfully" if exit_code == 0 else f"with error (Code: {exit_code})"
                msg = f"{CE_STOP} Script <code>{script_name}</code> stopped {status}."
                
                if exit_code != 0:
                    try:
                        with open(log_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            if lines:
                                last_lines = "".join(lines[-10:])
                                msg += f"\n\n<b>Last log output:</b>\n<pre>{html.escape(last_lines)}</pre>"
                    except:
                        pass
                
                safe_send(chat_id, msg)
        threading.Thread(target=monitor, daemon=True).start()
    except FileNotFoundError:
        safe_send(chat_id, f"{CE_CROSS} Node.js is not installed!")
    except Exception as e:
        safe_send(chat_id, f"{CE_CROSS} Error: {str(e)}")

# ==================== STYLED KEYBOARDS & MENUS ====================
def main_menu(user_id):
    is_admin = user_id in ADMIN_IDS or user_id == OWNER_ID
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    markup.add(
        CustomKeyboardButton("UPLOAD FILE", style="primary", icon_custom_emoji_id="5780773956030043338"),
        CustomKeyboardButton("MY SCRIPTS", style="primary", icon_custom_emoji_id="6033129724488715918")
    )
    markup.add(
        CustomKeyboardButton("INSTALL MODULE", style="primary", icon_custom_emoji_id="5987803826512466184"),
        CustomKeyboardButton("STATS", style="primary", icon_custom_emoji_id="6033118016407868078")
    )
    markup.add(
        CustomKeyboardButton("BUY PREMIUM", style="success", icon_custom_emoji_id="5767137507879685567"),
        CustomKeyboardButton("REDEEM CODE", style="success", icon_custom_emoji_id="6032819460346220361")
    )
    markup.add(
        CustomKeyboardButton("BOT SPEED", style="primary", icon_custom_emoji_id="5890847821728322055"),
        CustomKeyboardButton("HELP", style="primary", icon_custom_emoji_id="6282525354242348869")
    )
    markup.add(CustomKeyboardButton("MY PROFILE", style="primary", icon_custom_emoji_id="6035239240625820254"))
    if is_admin:
        markup.add(CustomKeyboardButton("SETTINGS & ADMIN", style="danger", icon_custom_emoji_id="5769547529993588669"))
    return markup

def force_join_menu(user_id=None, missing=None):
    channels = FORCE_CHANNELS
    if fc_show_mode() == 'unjoined' and user_id:
        channels = missing if missing is not None else get_missing_channels(user_id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    for ch in channels:
        url = channel_join_url(ch)
        if url:
            markup.add(CustomInlineKeyboardButton(f"JOIN {ch['name']}", url=url, style="primary", icon_custom_emoji_id="5780405967527089720"))
    for s in fc_social_links():
        markup.add(CustomInlineKeyboardButton(s['name'], url=s['url'], style="primary"))
    markup.add(CustomInlineKeyboardButton("VERIFY MEMBERSHIP", callback_data="check_join", style="success", icon_custom_emoji_id="6030437742066798869"))
    return markup

def script_control_menu(user_id, script_name, is_running):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.add(
            CustomInlineKeyboardButton("STOP", callback_data=f"stop_{user_id}_{script_name}", style="danger", icon_custom_emoji_id="6267262260243076354"),
            CustomInlineKeyboardButton("VIEW LOGS", callback_data=f"logs_{user_id}_{script_name}", style="primary", icon_custom_emoji_id="6030364658903293193")
        )
    else:
        markup.add(
            CustomInlineKeyboardButton("START", callback_data=f"start_{user_id}_{script_name}", style="success", icon_custom_emoji_id="6266829404849050968"),
            CustomInlineKeyboardButton("DELETE", callback_data=f"delete_{user_id}_{script_name}", style="danger", icon_custom_emoji_id="6035142758480482309"),
            CustomInlineKeyboardButton("VIEW LOGS", callback_data=f"logs_{user_id}_{script_name}", style="primary", icon_custom_emoji_id="6030364658903293193")
        )
    markup.add(CustomInlineKeyboardButton("BACK TO SCRIPTS", callback_data="back_to_scripts", style="primary", icon_custom_emoji_id="6264699552041801361"))
    return markup

def admin_panel_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        CustomInlineKeyboardButton("BOT STATS", callback_data="admin_stats", style="primary", icon_custom_emoji_id="6033118016407868078"),
        CustomInlineKeyboardButton("ALL USERS", callback_data="all_users", style="primary", icon_custom_emoji_id="6032819460346220361"),
        CustomInlineKeyboardButton("SET UPI ID", callback_data="set_upi_prompt", style="success", icon_custom_emoji_id="5987803826512466184"),
        CustomInlineKeyboardButton("SET UPLOAD CHANNEL", callback_data="set_upload_channel_prompt", style="success", icon_custom_emoji_id="5780405967527089720"),
        CustomInlineKeyboardButton("BAN USER", callback_data="ban_user_prompt", style="danger", icon_custom_emoji_id="6030331836763213973"),
        CustomInlineKeyboardButton("UNBAN USER", callback_data="unban_user_prompt", style="success", icon_custom_emoji_id="6030437742066798869"),
        CustomInlineKeyboardButton("CREATE REDEEM", callback_data="create_redeem_prompt", style="success", icon_custom_emoji_id="6032819460346220361"),
        CustomInlineKeyboardButton("MANAGE PLANS", callback_data="manage_plans", style="success", icon_custom_emoji_id="5767137507879685567"),
        CustomInlineKeyboardButton("GRANT PREMIUM", callback_data="grant_premium_prompt", style="success", icon_custom_emoji_id="6030437742066798869"),
        CustomInlineKeyboardButton("REMOVE PREMIUM", callback_data="admin_remove_premium", style="danger", icon_custom_emoji_id="6030331836763213973"),
        CustomInlineKeyboardButton("USER INFO", callback_data="admin_user_info", style="primary", icon_custom_emoji_id="6035239240625820254"),
        CustomInlineKeyboardButton("BACKUP", callback_data="admin_backup", style="success", icon_custom_emoji_id="6269214795325510848"),
        CustomInlineKeyboardButton("RESTORE", callback_data="admin_restore", style="danger", icon_custom_emoji_id="6264510702329797113"),
        CustomInlineKeyboardButton("FORCE CHANNELS", callback_data="manage_force_channels", style="primary", icon_custom_emoji_id="5780405967527089720"),
        CustomInlineKeyboardButton("MANAGE FILES", callback_data="manage_files", style="primary", icon_custom_emoji_id="6269214795325510848"),
        CustomInlineKeyboardButton("ALL FILES", callback_data="admin_all_files", style="primary", icon_custom_emoji_id="6269214795325510848"),
        CustomInlineKeyboardButton("RUNNING SCRIPTS", callback_data="admin_running_scripts", style="success", icon_custom_emoji_id="6266829404849050968"),
        CustomInlineKeyboardButton("BROADCAST", callback_data="admin_broadcast", style="primary", icon_custom_emoji_id="5780405967527089720"),
        CustomInlineKeyboardButton("MSG USER", callback_data="admin_msg_user", style="primary", icon_custom_emoji_id="6264777724741556322"),
        CustomInlineKeyboardButton("LOCK BOT", callback_data="lock_bot", style="danger", icon_custom_emoji_id="6282846669335702032"),
        CustomInlineKeyboardButton("UNLOCK BOT", callback_data="unlock_bot", style="success", icon_custom_emoji_id="6028551194861899805"),
        CustomInlineKeyboardButton("CLEAN LOGS", callback_data="clean_logs", style="danger", icon_custom_emoji_id="6035142758480482309"),
        CustomInlineKeyboardButton("CLOSE", callback_data="admin_close", style="danger", icon_custom_emoji_id="6030331836763213973")
    )
    return markup

# ==================== BOT COMMANDS ====================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type != 'private':
        return

    user_id = message.from_user.id
    if is_user_banned(user_id):
        safe_send(message.chat.id, f"{CE_SKULL} <b>Access Denied:</b> You have been banned from using this bot.")
        return

    user_name = message.from_user.first_name
    register_user(message.from_user)

    user_dir_path = os.path.join(UPLOAD_DIR, str(user_id))
    is_new_user = not os.path.exists(user_dir_path)

    if is_new_user:
        os.makedirs(user_dir_path, exist_ok=True)
        raw_username = f"@{message.from_user.username}" if message.from_user.username else "No Username"
        safe_u_name = html.escape(user_name)
        safe_uname = html.escape(raw_username)
        is_premium_str = "Yes" if getattr(message.from_user, 'is_premium', False) else "No"

        notify_markup = types.InlineKeyboardMarkup()
        notify_markup.add(CustomInlineKeyboardButton("Talk to User", url=f"tg://user?id={user_id}", style="primary", icon_custom_emoji_id="6264777724741556322"))

        notify_text = (
            f"{CE_STAR} <b>New User Started Bot</b>\n\n"
            f"{CE_SPARKLE} <b>Name:</b> {safe_u_name}\n"
            f"{CE_PIN} <b>Username:</b> {safe_uname}\n"
            f"{CE_ID} <b>Chat ID:</b> <code>{user_id}</code>\n"
            f"{CE_DIAMOND} <b>Telegram Premium:</b> {is_premium_str}"
        )

        for admin_id in ADMIN_IDS:
            safe_send(admin_id, notify_text, reply_markup=notify_markup)
        if OWNER_ID not in ADMIN_IDS:
            safe_send(OWNER_ID, notify_text, reply_markup=notify_markup)
        post_to_setting_channel('newuser_channel', f"⭐ <b>New User Started Bot</b>\n✨ Name: {safe_u_name}\n📌 Username: {safe_uname}\n🆔 ID: <code>{user_id}</code>")

    missing = get_missing_channels(user_id)
    if missing:
        shown = missing if fc_show_mode() == 'unjoined' else FORCE_CHANNELS
        channels_text = ""
        for ch in shown:
            mark = CE_CROSS if ch in missing else CE_CHECK
            channels_text += f"{mark} <b>{html.escape(str(ch['name']))}</b>\n"
            
        welcome_text = (
            f"<b>{CE_CROWN} SCRIPT HOSTING BOT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{CE_SPARKLE} <b>Welcome {html.escape(user_name)}!</b> {CE_SPARKLE}\n\n"
            f"{CE_WARN} <b>IMPORTANT NOTICE:</b>\n"
            "You must join all required channels and groups below to use this bot.\n\n"
            f"{channels_text}\n"
            "<i>After joining, click the verify button below.</i>"
        )
        safe_send(message.chat.id, welcome_text, reply_markup=force_join_menu(user_id, missing))
        return

    scripts = get_user_scripts(user_id)
    running_count = sum(1 for s in scripts if is_script_running(user_id, s))
    user_status = f"{CE_DIAMOND} <b>PREMIUM MEMBER</b>" if is_user_premium(user_id) else f"{CE_PACKAGE} <b>NORMAL USER</b> (Limit: 1 Script)"

    welcome_text = (
        f"<b>{CE_CROWN} SCRIPT HOSTING BOT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{user_status}\n\n"
        f"{CE_SPARKLE} <b>Name:</b> {html.escape(user_name)}\n"
        f"{CE_ID} <b>ID:</b> <code>{user_id}</code>\n\n"
        f"{CE_STATS} <b>YOUR STATISTICS:</b>\n"
        f" ├ Active Scripts: <b>{len(scripts)}</b>\n"
        f" ├ {CE_GREEN} Running: <b>{running_count}</b>\n"
        f" └ {CE_RED} Stopped: <b>{len(scripts) - running_count}</b>\n\n"
        "<i>Use the buttons below to manage your scripts.</i>"
    )

    safe_send(message.chat.id, welcome_text, reply_markup=main_menu(user_id))

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join_callback(call):
    user_id = call.from_user.id
    if is_user_banned(user_id):
        safe_callback(call.id, "You are banned!", True)
        return

    if is_user_joined(user_id):
        safe_callback(call.id, "Verification Successful!", True)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        call.message.from_user = call.from_user
        send_welcome(call.message)
    else:
        safe_callback(call.id, "Please join all required channels and groups first!", True)

# ==================== ADMIN: SET UPLOAD CHANNEL ====================
@bot.callback_query_handler(func=lambda call: call.data == "set_upload_channel_prompt")
def set_upload_channel_prompt(call):
    if call.from_user.id not in ADMIN_IDS and call.from_user.id != OWNER_ID:
        safe_callback(call.id, "Admin only!", True)
        return
    
    safe_callback(call.id)
    admin_temp_state[call.from_user.id] = "waiting_upload_channel_input"
    
    current_channel = BOT_SETTINGS.get("upload_channel", "Not Set")
    text = (
        f"<b>{CE_BROADCAST} SET UPLOAD CHANNEL</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Current Upload Channel: <code>{current_channel}</code>\n\n"
        "Send the new Channel Username (e.g., <code>@myfileschannel</code>) or ID (e.g., <code>-100xxxxxxxxxx</code>):\n\n"
        "<i>Send /cancel to abort.</i>"
    )
    msg = safe_send(call.message.chat.id, text)
    if msg:
        bot.register_next_step_handler(msg, process_set_upload_channel)

def process_set_upload_channel(message):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS and admin_id != OWNER_ID:
        return
    if is_cancel_command(message):
        if admin_id in admin_temp_state:
            del admin_temp_state[admin_id]
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return

    channel_input = message.text.strip()
    if not channel_input:
        safe_send(message.chat.id, f"{CE_CROSS} Invalid input.")
        return

    if admin_id in admin_temp_state:
        del admin_temp_state[admin_id]

    BOT_SETTINGS["upload_channel"] = channel_input
    save_settings(BOT_SETTINGS)

    safe_send(message.chat.id, f"{CE_CHECK} Upload channel successfully updated to: <code>{channel_input}</code>")

# ==================== ADMIN: SET UPI ID ====================
@bot.callback_query_handler(func=lambda call: call.data == "set_upi_prompt")
def set_upi_prompt(call):
    if call.from_user.id not in ADMIN_IDS and call.from_user.id != OWNER_ID:
        safe_callback(call.id, "Admin only!", True)
        return
    
    safe_callback(call.id)
    admin_temp_state[call.from_user.id] = "waiting_upi_input"
    
    current_upi = BOT_SETTINGS.get("upi_id", "Not Set")
    text = (
        f"<b>{CE_DIAMOND} SET UPI ID FOR PAYMENTS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Current UPI ID: <code>{current_upi}</code>\n\n"
        "Send the new UPI ID (e.g., <code>yourname@oksbi</code>):\n\n"
        "<i>Send /cancel to abort.</i>"
    )
    msg = safe_send(call.message.chat.id, text)
    if msg:
        bot.register_next_step_handler(msg, process_set_upi)

def process_set_upi(message):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS and admin_id != OWNER_ID:
        return
    if is_cancel_command(message):
        if admin_id in admin_temp_state:
            del admin_temp_state[admin_id]
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return

    upi_id = message.text.strip()
    if not upi_id:
        safe_send(message.chat.id, f"{CE_CROSS} Invalid UPI ID.")
        return

    if admin_id in admin_temp_state:
        del admin_temp_state[admin_id]

    BOT_SETTINGS["upi_id"] = upi_id
    save_settings(BOT_SETTINGS)

    safe_send(message.chat.id, f"{CE_CHECK} UPI ID successfully updated to: <code>{upi_id}</code>")

# ==================== BUY PREMIUM & SCREENSHOT PAYMENT FLOW ====================
@bot.message_handler(func=lambda message: message.text == 'BUY PREMIUM' and message.chat.type == 'private')
def show_buy_premium(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        safe_send(message.chat.id, f"{CE_SKULL} <b>Access Denied:</b> You are banned.")
        return
    if not is_user_joined(user_id):
        send_welcome(message)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for plan in PLANS:
        markup.add(CustomInlineKeyboardButton(f"✨ Buy {plan['name']} ({plan['price']})", callback_data=f"buyplan_{plan['id']}", style="success", icon_custom_emoji_id="5767137507879685567"))
    
    text = (
        f"<b>{CE_DIAMOND} UPGRADE TO PREMIUM</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{CE_CHECK} <b>Benefits of Premium:</b>\n"
        " ├ Upload & Run **Unlimited Files/Scripts**\n"
        " ├ Priority Support\n"
        " └ No Restrictions\n\n"
        "<b>Select a plan below to purchase:</b>"
    )
    safe_send(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buyplan_"))
def handle_buy_plan_callback(call):
    plan_id = call.data.split("_", 1)[1]
    plan = next((p for p in PLANS if p['id'] == plan_id), None)
    if not plan:
        safe_callback(call.id, "Plan not found!", True)
        return
    
    safe_callback(call.id)
    upi_id = BOT_SETTINGS.get("upi_id", "merchant@upi")
    
    qr_text = f"upi://pay?pa={upi_id}&pn=ScriptHostingBot&am=&cu=INR"
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={qr_text}"

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(CustomInlineKeyboardButton("📤 Send Payment Screenshot", callback_data=f"send_ss_{plan['id']}", style="success", icon_custom_emoji_id="6264777724741556322"))

    caption = (
        f"<b>{CE_DIAMOND} PAYMENT GATEWAY</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📦 <b>Plan:</b> {plan['name']}\n"
        f"💰 <b>Price:</b> {plan['price']}\n\n"
        f"🏦 <b>UPI ID:</b> <code>{upi_id}</code>\n\n"
        "<i>Scan the QR code above or pay directly via UPI ID.\n"
        "After paying, click the button below to send your payment screenshot!</i>"
    )

    try:
        bot.send_photo(call.message.chat.id, qr_url, caption=caption, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        safe_send(call.message.chat.id, f"{caption}\n\nScan QR failed, pay to UPI ID: <code>{upi_id}</code>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("send_ss_"))
def send_screenshot_prompt(call):
    plan_id = call.data.split("_", 2)[2]
    safe_callback(call.id)
    user_id = call.from_user.id
    screenshot_waiting[user_id] = plan_id

    safe_send(
        call.message.chat.id,
        f"<b>{CE_MAIL} UPLOAD SCREENSHOT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Please send your payment screenshot photo now.\n\n"
        "<i>Send /cancel to abort.</i>"
    )

@bot.message_handler(content_types=['photo'], func=lambda m: m.from_user.id in screenshot_waiting)
def handle_payment_screenshot(message):
    user_id = message.from_user.id
    plan_id = screenshot_waiting[user_id]
    del screenshot_waiting[user_id]

    plan = next((p for p in PLANS if p['id'] == plan_id), None)
    plan_name = plan['name'] if plan else "Custom Plan"
    days = plan['days'] if plan else 1

    photo_id = message.photo[-1].file_id
    user_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "No Username"

    short_id = str(uuid.uuid4())[:8]
    user_temp_data[short_id] = {"user_id": user_id, "days": days}

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        CustomInlineKeyboardButton("Approve", callback_data=f"approve_pay_{short_id}", style="success", icon_custom_emoji_id="6030437742066798869"),
        CustomInlineKeyboardButton("Reject", callback_data=f"reject_pay_{short_id}", style="danger", icon_custom_emoji_id="6030331836763213973")
    )

    admin_caption = (
        f"{CE_DIAMOND} <b>New Payment Screenshot Received</b>\n\n"
        f"{CE_SPARKLE} <b>User:</b> {html.escape(user_name)} ({username})\n"
        f"{CE_ID} <b>Chat ID:</b> <code>{user_id}</code>\n"
        f"{CE_PACKAGE} <b>Plan:</b> {plan_name} ({days} Days)"
    )

    for admin_id in ADMIN_IDS:
        bot.send_photo(admin_id, photo_id, caption=admin_caption, parse_mode="HTML", reply_markup=markup)
    if OWNER_ID not in ADMIN_IDS:
        bot.send_photo(OWNER_ID, photo_id, caption=admin_caption, parse_mode="HTML", reply_markup=markup)

    safe_send(message.chat.id, f"{CE_CHECK} Payment screenshot sent successfully to admin! Please wait for approval.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_pay_"))
def approve_payment_callback(call):
    short_id = call.data.split("_")[2]
    if short_id not in user_temp_data:
        safe_callback(call.id, "Request expired or handled!", True)
        return

    data = user_temp_data[short_id]
    target_id = data["user_id"]
    days = data["days"]
    del user_temp_data[short_id]

    str_uid = str(target_id)
    if str_uid not in USERS_DB:
        USERS_DB[str_uid] = {}

    current_expiry = USERS_DB[str_uid].get("premium_expiry")
    base_time = datetime.now()
    if current_expiry:
        try:
            exp_dt = datetime.fromisoformat(current_expiry)
            if exp_dt > base_time:
                base_time = exp_dt
        except:
            pass

    new_expiry = base_time + timedelta(days=days)
    USERS_DB[str_uid]["premium_expiry"] = new_expiry.isoformat()
    save_db(USERS_DB)

    post_to_setting_channel('payout_channel', f"✅ <b>Premium Payment Approved</b>\n🆔 User: <code>{target_id}</code>\n📅 Plan: {days} days")
    safe_callback(call.id, "Payment Approved!", True)
    try:
        bot.edit_message_caption(
            caption=f"{call.message.caption}\n\n{CE_CHECK} <b>Status: APPROVED</b>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    except:
        pass

    safe_send(target_id, f"<b>{CE_DIAMOND} PAYMENT APPROVED!</b>\n━━━━━━━━━━━━━━━━━━━━\n\nYour payment has been verified by the admin. You have been granted **Premium** for <b>{days} Days</b>!\nNew Expiry: {new_expiry.strftime('%Y-%m-%d %H:%M')}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_pay_"))
def reject_payment_callback(call):
    short_id = call.data.split("_")[2]
    if short_id in user_temp_data:
        target_id = user_temp_data[short_id]["user_id"]
        del user_temp_data[short_id]
        safe_send(target_id, f"{CE_CROSS} <b>Payment Rejected:</b> Your payment screenshot was declined by the admin. Contact support if this is an error.")

    safe_callback(call.id, "Payment Rejected!", True)
    try:
        bot.edit_message_caption(
            caption=f"{call.message.caption}\n\n{CE_CROSS} <b>Status: REJECTED</b>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    except:
        pass

# ==================== ADMIN: BAN & UNBAN SYSTEM ====================
@bot.callback_query_handler(func=lambda call: call.data == "ban_user_prompt")
def ban_user_prompt(call):
    if call.from_user.id not in ADMIN_IDS and call.from_user.id != OWNER_ID:
        safe_callback(call.id, "Admin only!", True)
        return
    
    safe_callback(call.id)
    admin_temp_state[call.from_user.id] = "waiting_ban_uid"
    
    text = (
        f"<b>{CE_SKULL} BAN USER</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send the <code>USER_ID</code> you want to ban:\n\n"
        "<i>Send /cancel to abort.</i>"
    )
    msg = safe_send(call.message.chat.id, text)
    if msg:
        bot.register_next_step_handler(msg, process_ban_user)

def process_ban_user(message):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS and admin_id != OWNER_ID:
        return
    if is_cancel_command(message):
        if admin_id in admin_temp_state:
            del admin_temp_state[admin_id]
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return

    target_id = message.text.strip()
    if not target_id.isdigit():
        safe_send(message.chat.id, f"{CE_CROSS} Invalid User ID. Must be numeric digits.")
        return

    if admin_id in admin_temp_state:
        del admin_temp_state[admin_id]

    global BANNED_USERS
    BANNED_USERS = load_banned_users()
    if int(target_id) in [int(x) for x in BANNED_USERS]:
        safe_send(message.chat.id, f"{CE_WARN} User <code>{target_id}</code> is already banned.")
        return

    BANNED_USERS.append(int(target_id))
    save_banned_users(BANNED_USERS)

    safe_send(message.chat.id, f"{CE_CHECK} User <code>{target_id}</code> has been successfully banned!")
    try:
        safe_send(int(target_id), f"{CE_SKULL} <b>You have been banned by the admin!</b>")
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == "unban_user_prompt")
def unban_user_prompt(call):
    if call.from_user.id not in ADMIN_IDS and call.from_user.id != OWNER_ID:
        safe_callback(call.id, "Admin only!", True)
        return
    
    safe_callback(call.id)
    admin_temp_state[call.from_user.id] = "waiting_unban_uid"
    
    text = (
        f"<b>{CE_CHECK} UNBAN USER</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send the <code>USER_ID</code> you want to unban:\n\n"
        "<i>Send /cancel to abort.</i>"
    )
    msg = safe_send(call.message.chat.id, text)
    if msg:
        bot.register_next_step_handler(msg, process_unban_user)

def process_unban_user(message):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS and admin_id != OWNER_ID:
        return
    if is_cancel_command(message):
        if admin_id in admin_temp_state:
            del admin_temp_state[admin_id]
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return

    target_id = message.text.strip()
    if not target_id.isdigit():
        safe_send(message.chat.id, f"{CE_CROSS} Invalid User ID. Must be numeric digits.")
        return

    if admin_id in admin_temp_state:
        del admin_temp_state[admin_id]

    global BANNED_USERS
    BANNED_USERS = load_banned_users()
    
    target_int = int(target_id)
    if target_int in BANNED_USERS or str(target_int) in [str(x) for x in BANNED_USERS]:
        BANNED_USERS = [x for x in BANNED_USERS if int(x) != target_int]
        save_banned_users(BANNED_USERS)
        safe_send(message.chat.id, f"{CE_CHECK} User <code>{target_id}</code> has been successfully unbanned!")
        try:
            safe_send(target_int, f"{CE_CHECK} <b>You have been unbanned by the admin! You can use the bot now.</b>")
        except:
            pass
    else:
        safe_send(message.chat.id, f"{CE_WARN} User <code>{target_id}</code> was not in the banned list.")

# ==================== REDEEM CODE USER FLOW ====================
@bot.message_handler(func=lambda message: message.text == 'REDEEM CODE' and message.chat.type == 'private')
def redeem_code_prompt(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        safe_send(message.chat.id, f"{CE_SKULL} <b>Access Denied:</b> You are banned.")
        return
    if not is_user_joined(user_id):
        send_welcome(message)
        return
    
    msg = safe_send(
        message.chat.id,
        f"<b>{CE_DIAMOND} REDEEM PREMIUM CODE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Please enter your redeem code below:\n\n"
        "<i>Send /cancel to abort.</i>"
    )
    if msg:
        bot.register_next_step_handler(msg, process_redeem_code)

def process_redeem_code(message):
    user_id = message.from_user.id
    if is_cancel_command(message):
        safe_send(message.chat.id, f"{CE_CROSS} Action cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return

    code = message.text.strip()
    global REDEEM_CODES
    REDEEM_CODES = load_redeem_codes()

    if code not in REDEEM_CODES:
        msg = safe_send(message.chat.id, f"{CE_CROSS} Invalid or expired redeem code!\n\n<i>Try again or send /cancel:</i>")
        if msg:
            bot.register_next_step_handler(msg, process_redeem_code)
        return

    days = REDEEM_CODES[code]
    del REDEEM_CODES[code]
    save_redeem_codes(REDEEM_CODES)

    str_uid = str(user_id)
    if str_uid not in USERS_DB:
        USERS_DB[str_uid] = {}

    current_expiry = USERS_DB[str_uid].get("premium_expiry")
    base_time = datetime.now()
    if current_expiry:
        try:
            exp_dt = datetime.fromisoformat(current_expiry)
            if exp_dt > base_time:
                base_time = exp_dt
        except:
            pass

    new_expiry = base_time + timedelta(days=days)
    USERS_DB[str_uid]["premium_expiry"] = new_expiry.isoformat()
    save_db(USERS_DB)

    safe_send(
        message.chat.id,
        f"<b>{CE_CHECK} REDEEM SUCCESSFUL!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"You have successfully redeemed <b>{days} Days</b> of Premium!\n"
        f"New Expiry: <b>{new_expiry.strftime('%Y-%m-%d %H:%M')}</b>\n\n"
        "<i>Enjoy unlimited script hosting!</i>",
        reply_markup=main_menu(user_id)
    )

# ==================== ADMIN: CREATE REDEEM CODE ====================
@bot.callback_query_handler(func=lambda call: call.data == "create_redeem_prompt")
def create_redeem_prompt(call):
    if call.from_user.id not in ADMIN_IDS and call.from_user.id != OWNER_ID:
        safe_callback(call.id, "Admin only!", True)
        return
    
    safe_callback(call.id)
    admin_temp_state[call.from_user.id] = "waiting_redeem_input"
    
    text = (
        f"<b>{CE_DIAMOND} CREATE REDEEM CODE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send code details in this exact format:\n"
        "<code>CODE | Days</code>\n\n"
        "<b>Example:</b>\n"
        "<code>AADITYA30 | 30</code>\n\n"
        "<i>Or send just number of days (e.g. <code>7</code>) to auto-generate a random code.</i>\n\n"
        "<i>Send /cancel to abort.</i>"
    )
    msg = safe_send(call.message.chat.id, text)
    if msg:
        bot.register_next_step_handler(msg, process_create_redeem_input)

def process_create_redeem_input(message):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS and admin_id != OWNER_ID:
        return
        
    if is_cancel_command(message):
        if admin_id in admin_temp_state:
            del admin_temp_state[admin_id]
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return

    text = message.text.strip()
    global REDEEM_CODES
    REDEEM_CODES = load_redeem_codes()

    code = ""
    days = 0

    if '|' in text:
        parts = [p.strip() for p in text.split('|')]
        if len(parts) == 2 and parts[1].isdigit():
            code = parts[0]
            days = int(parts[1])
    elif text.isdigit():
        days = int(text)
        code = f"PREM-{str(uuid.uuid4())[:6].upper()}"

    if not code or days <= 0:
        msg = safe_send(message.chat.id, f"{CE_CROSS} Invalid format! Use <code>CODE | Days</code> or just number of days.\n\n<i>Try again or send /cancel:</i>")
        if msg:
            bot.register_next_step_handler(msg, process_create_redeem_input)
        return

    if admin_id in admin_temp_state:
        del admin_temp_state[admin_id]

    REDEEM_CODES[code] = days
    save_redeem_codes(REDEEM_CODES)

    safe_send(
        message.chat.id,
        f"<b>{CE_CHECK} REDEEM CODE CREATED!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Code: <code>{code}</code>\n"
        f"Duration: <b>{days} Days</b>\n\n"
        "<i>Users can now use this code in 'REDEEM CODE' menu.</i>",
        reply_markup=admin_panel_menu()
    )

# ==================== ADMIN: MANAGE PLANS ====================
@bot.callback_query_handler(func=lambda call: call.data == "manage_plans")
def manage_plans_callback(call):
    if call.from_user.id not in ADMIN_IDS and call.from_user.id != OWNER_ID:
        safe_callback(call.id, "Admin only!", True)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for idx, plan in enumerate(PLANS):
        markup.add(CustomInlineKeyboardButton(f"❌ Delete: {plan['name']} ({plan['price']})", callback_data=f"remove_plan_{idx}", style="danger", icon_custom_emoji_id="6035142758480482309"))
        
    markup.add(CustomInlineKeyboardButton("➕ Add New Plan", callback_data="add_plan_prompt", style="success", icon_custom_emoji_id="6030437742066798869"))
    markup.add(CustomInlineKeyboardButton("⬅️ Back to Admin Panel", callback_data="admin_back", style="primary", icon_custom_emoji_id="6264699552041801361"))
    
    text = (
        f"<b>{CE_DIAMOND} PREMIUM PLANS MANAGER</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Total Plans: <b>{len(PLANS)}</b>\n\n"
        "<i>Manage or add pricing plans below:</i>"
    )
    safe_callback(call.id)
    safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("remove_plan_"))
def remove_plan_callback(call):
    if call.from_user.id not in ADMIN_IDS and call.from_user.id != OWNER_ID:
        safe_callback(call.id, "Admin only!", True)
        return
    
    idx = int(call.data.split("_")[2])
    if 0 <= idx < len(PLANS):
        removed = PLANS.pop(idx)
        save_plans(PLANS)
        safe_callback(call.id, f"Removed plan {removed['name']}!", True)
    else:
        safe_callback(call.id, "Invalid plan index!", True)
    manage_plans_callback(call)

@bot.callback_query_handler(func=lambda call: call.data == "add_plan_prompt")
def add_plan_prompt(call):
    if call.from_user.id not in ADMIN_IDS and call.from_user.id != OWNER_ID:
        safe_callback(call.id, "Admin only!", True)
        return
    
    safe_callback(call.id)
    admin_temp_state[call.from_user.id] = "waiting_plan_details"
    
    text = (
        f"<b>{CE_DIAMOND} ADD NEW PLAN</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send the plan details in this exact format:\n"
        "<code>Plan Name | Price | Days</code>\n\n"
        "<b>Example:</b>\n"
        "<code>15 Days Pack | ₹150 | 15</code>\n\n"
        "<i>Send /cancel to abort.</i>"
    )
    msg = safe_send(call.message.chat.id, text)
    if msg:
        bot.register_next_step_handler(msg, process_add_plan_input)

def process_add_plan_input(message):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS and admin_id != OWNER_ID:
        return
        
    if is_cancel_command(message):
        if admin_id in admin_temp_state:
            del admin_temp_state[admin_id]
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return

    text = message.text.strip()
    parts = [p.strip() for p in text.split('|')]
    if len(parts) != 3 or not parts[2].isdigit():
        msg = safe_send(message.chat.id, f"{CE_CROSS} Invalid format! Use: <code>Plan Name | Price | Days</code>\n\n<i>Try again or send /cancel:</i>")
        if msg:
            bot.register_next_step_handler(msg, process_add_plan_input)
        return

    if admin_id in admin_temp_state:
        del admin_temp_state[admin_id]

    plan_name, price, days = parts[0], parts[1], int(parts[2])
    plan_id = f"plan_{int(time.time())}"

    PLANS.append({"id": plan_id, "name": plan_name, "price": price, "days": days})
    save_plans(PLANS)

    safe_send(message.chat.id, f"{CE_CHECK} Successfully added plan <b>{plan_name}</b> ({price}) for {days} days!")
    fake_call = type('obj', (object,), {'from_user': message.from_user, 'message': message, 'id': '0'})
    manage_plans_callback(fake_call)

# ==================== ADMIN: GRANT PREMIUM ====================
@bot.callback_query_handler(func=lambda call: call.data == "grant_premium_prompt")
def grant_premium_prompt(call):
    if call.from_user.id not in ADMIN_IDS and call.from_user.id != OWNER_ID:
        safe_callback(call.id, "Admin only!", True)
        return
    
    safe_callback(call.id)
    admin_temp_state[call.from_user.id] = "waiting_grant_uid"
    
    text = (
        f"<b>{CE_DIAMOND} GRANT PREMIUM TO USER</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send the target <code>USER_ID</code>:\n\n"
        "<i>Send /cancel to cancel.</i>"
    )
    msg = safe_send(call.message.chat.id, text)
    if msg:
        bot.register_next_step_handler(msg, process_grant_uid)

def process_grant_uid(message):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS and admin_id != OWNER_ID:
        return
    if is_cancel_command(message):
        if admin_id in admin_temp_state:
            del admin_temp_state[admin_id]
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return

    target_id = message.text.strip()
    if not target_id.isdigit():
        safe_send(message.chat.id, f"{CE_CROSS} Invalid User ID. Must be numeric digits.")
        return

    admin_temp_state[admin_id] = {"state": "waiting_grant_days", "target_id": target_id}
    msg = safe_send(message.chat.id, f"User ID: <code>{target_id}</code> accepted.\n\nNow send the <b>number of days</b> for premium (e.g. <code>30</code>):\n<i>Send /cancel to cancel.</i>")
    if msg:
        bot.register_next_step_handler(msg, process_grant_days)

def process_grant_days(message):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS and admin_id != OWNER_ID:
        return
    if is_cancel_command(message):
        if admin_id in admin_temp_state:
            del admin_temp_state[admin_id]
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return

    days_text = message.text.strip()
    if not days_text.isdigit():
        safe_send(message.chat.id, f"{CE_CROSS} Invalid days number. Must be numeric.")
        return

    days = int(days_text)
    data = admin_temp_state.get(admin_id)
    if not isinstance(data, dict):
        safe_send(message.chat.id, f"{CE_CROSS} Session expired. Start over from Admin Panel.")
        return

    target_id = data["target_id"]
    if admin_id in admin_temp_state:
        del admin_temp_state[admin_id]

    str_uid = str(target_id)
    if str_uid not in USERS_DB:
        USERS_DB[str_uid] = {}

    expiry_date = datetime.now() + timedelta(days=days)
    USERS_DB[str_uid]["premium_expiry"] = expiry_date.isoformat()
    save_db(USERS_DB)

    safe_send(message.chat.id, f"{CE_CHECK} Successfully granted premium to <code>{target_id}</code> for <b>{days} days</b>!")
    try:
        safe_send(int(target_id), f"<b>{CE_DIAMOND} CONGRATULATIONS!</b>\n━━━━━━━━━━━━━━━━━━━━\n\nAdmin has granted you **Premium Membership** for <b>{days} days</b>!\nYou can now run unlimited scripts simultaneously.")
    except:
        pass

# ==================== FORCE JOIN SYSTEM (channels + social links) ====================
fc_pending = {}   # admin_id -> {'lines': [], 'seen': set(), 'timer': Timer, 'chat_id': int}
_BOT_ID = {}

def get_bot_id():
    if 'id' not in _BOT_ID:
        _BOT_ID['id'] = bot.get_me().id
    return _BOT_ID['id']

def fc_social_links():
    return BOT_SETTINGS.setdefault('social_links', [])

def fc_show_mode():
    return BOT_SETTINGS.get('force_show_mode', 'all')

def short_label(text, n=13):
    text = str(text)
    return text if len(text) <= n else text[:n - 1] + '…'

def chat_key(raw):
    raw = str(raw)
    return int(raw) if raw.lstrip('-').isdigit() else raw

def normalize_url(url):
    url = url.strip()
    if url.lower().startswith(('t.me/', 'telegram.me/')):
        url = 'https://' + url
    return url

def valid_url(url):
    return bool(re.match(r'^https?://[^\s/]+\.[^\s/]+\S*$', url))

def valid_tg_link(url):
    return bool(re.match(r'^https?://(t\.me|telegram\.me)/\S+$', url))

def resolve_chat(raw):
    raw = raw.strip()
    m = re.match(r'^(?:https?://)?t\.me/([A-Za-z][A-Za-z0-9_]{3,})/?$', raw)
    if m:
        raw = '@' + m.group(1)
    if not (raw.startswith('@') or raw.lstrip('-').isdigit()):
        raise ValueError("invalid")
    return bot.get_chat(chat_key(raw))

def extract_chats(message):
    """Chats from a forwarded message, or from @usernames / chat ids in the text."""
    chats, errors = [], []
    fchat = getattr(message, 'forward_from_chat', None)
    if fchat is None:
        origin = getattr(message, 'forward_origin', None)
        fchat = getattr(origin, 'chat', None) if origin else None
    if fchat is not None:
        chats.append(fchat)
    elif message.text:
        for tok in re.split(r'[\s,]+', message.text.strip()):
            if not tok:
                continue
            try:
                chats.append(resolve_chat(tok))
            except Exception:
                errors.append(tok)
    return chats, errors

def bot_is_admin_in(chat_id):
    try:
        me = bot.get_chat_member(chat_id, get_bot_id())
        return me.status in ('administrator', 'creator')
    except Exception:
        return False

def add_force_channel_entry(chat):
    cid = str(chat.id)
    uname = getattr(chat, 'username', None) or ''
    for c in FORCE_CHANNELS:
        if str(c['id']) == cid or (uname and str(c['id']).lower() == '@' + uname.lower()):
            return 'dup', f"{cid} (already added)"
    entry = {"id": cid, "name": getattr(chat, 'title', None) or uname or cid,
             "username": uname, "link": f"https://t.me/{uname}" if uname else ""}
    note = ""
    if not bot_is_admin_in(chat.id):
        note = " ⚠️ bot is not admin there (verification needs admin)"
    elif not uname:
        try:
            entry["link"] = bot.export_chat_invite_link(chat.id)
        except Exception:
            pass
    FORCE_CHANNELS.append(entry)
    save_force_channels(FORCE_CHANNELS)
    return 'added', cid + note

def channel_join_url(ch):
    link = (ch.get('link') or '').strip()
    if link:
        return link
    cid = str(ch['id'])
    if cid.startswith('@'):
        return f"https://t.me/{cid[1:]}"
    if ch.get('username'):
        return f"https://t.me/{ch['username']}"
    try:   # private channel without a saved link: try to create one
        link = bot.export_chat_invite_link(chat_key(cid))
        ch['link'] = link
        save_force_channels(FORCE_CHANNELS)
        return link
    except Exception:
        return None

def get_missing_channels(user_id):
    missing = []
    for ch in FORCE_CHANNELS:
        try:
            m = bot.get_chat_member(chat_key(ch['id']), user_id)
            ok = m.status in ('member', 'administrator', 'creator') or (m.status == 'restricted' and getattr(m, 'is_member', False))
        except Exception:
            ok = False
        if not ok:
            missing.append(ch)
    return missing

def post_to_setting_channel(key, text):
    ch = BOT_SETTINGS.get(key)
    if not ch:
        return
    try:
        bot.send_message(chat_key(ch['id']), text, parse_mode='HTML')
    except Exception as e:
        print(f"Post to {key} failed: {e}")

# ---------- admin panel ----------
def fc_panel(chat_id, msg_id=None):
    socials, channels = fc_social_links(), FORCE_CHANNELS
    markup = types.InlineKeyboardMarkup(row_width=5)
    for i, s in enumerate(socials):
        markup.row(
            CustomInlineKeyboardButton(short_label(s['name']), callback_data=f"fc_s_{i}_edit", style="primary"),
            CustomInlineKeyboardButton("❌", callback_data=f"fc_s_{i}_del", style="danger"),
            CustomInlineKeyboardButton("🔼", callback_data=f"fc_s_{i}_up", style="primary"),
            CustomInlineKeyboardButton("🔽", callback_data=f"fc_s_{i}_dn", style="primary"),
            CustomInlineKeyboardButton("👀", callback_data=f"fc_s_{i}_info", style="primary"))
    for i, ch in enumerate(channels):
        markup.row(
            CustomInlineKeyboardButton(short_label(ch.get('name') or ch['id']), callback_data=f"fc_c_{i}_link", style="primary"),
            CustomInlineKeyboardButton("❌", callback_data=f"fc_c_{i}_del", style="danger"),
            CustomInlineKeyboardButton("🔼", callback_data=f"fc_c_{i}_up", style="primary"),
            CustomInlineKeyboardButton("🔽", callback_data=f"fc_c_{i}_dn", style="primary"),
            CustomInlineKeyboardButton("👀", callback_data=f"fc_c_{i}_info", style="primary"))
    mode_text = "All Channels" if fc_show_mode() == 'all' else "Not Joined Only"
    markup.add(CustomInlineKeyboardButton("Add Channels", callback_data="fc_add_ch", style="success"))
    markup.add(CustomInlineKeyboardButton("Add Payout Channel", callback_data="fc_add_payout", style="success"))
    markup.add(CustomInlineKeyboardButton("Add Social Media Links", callback_data="fc_add_social", style="success"))
    markup.add(CustomInlineKeyboardButton("📢 Broadcast To Channels", callback_data="fc_broadcast", style="primary"))
    markup.add(CustomInlineKeyboardButton("⚡ New User Join Channels", callback_data="fc_newuser", style="primary"))
    markup.add(CustomInlineKeyboardButton(f"⚪ Show Mode: {mode_text}", callback_data="fc_mode", style="primary"))
    markup.add(CustomInlineKeyboardButton("⬅ Back", callback_data="admin_back", style="danger"))
    if not socials and not channels:
        text = ("⚠️ <b>No Channels Or Social Links Added Yet.</b>\n\n"
                "💡 Click 'Add Channels' Or 'Add Social Link' To Add New Channels And Social Links.")
    else:
        text = ("📢 <b>Here You Can Manage Your Channels And Social Links</b>\n\n"
                "Click On A Channel Or Social Link To Set An Invite Link For Private Channels And Edit Social Link.")
    if msg_id:
        safe_edit(chat_id, msg_id, text, reply_markup=markup)
    else:
        safe_send(chat_id, text, reply_markup=markup)

def fc_cancelled(message):
    safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
    if message.text in MENU_COMMANDS:
        route_menu_command(message)

# ---------- add channels (username / id / forwarded messages, multiple) ----------
def process_fc_add_channels(message):
    admin_id = message.from_user.id
    if not is_admin_user(admin_id):
        return
    if is_cancel_command(message):
        pend = fc_pending.pop(admin_id, None)
        if pend and pend.get('timer'):
            pend['timer'].cancel()
        fc_cancelled(message)
        return
    chats, errors = extract_chats(message)
    if not chats and not errors:
        msg = safe_send(message.chat.id, f"{CE_CROSS} Send a channel Username (with @), Chat ID, or forward a message from the channel.\n<i>/cancel to abort.</i>")
        if msg:
            bot.register_next_step_handler(msg, process_fc_add_channels)
        return
    pend = fc_pending.setdefault(admin_id, {'lines': [], 'seen': set(), 'timer': None, 'chat_id': message.chat.id, 'added': [], 'warn': []})
    for chat in chats:
        cid = str(chat.id)
        if cid in pend['seen']:
            continue
        pend['seen'].add(cid)
        try:
            status, line = add_force_channel_entry(chat)
        except Exception as e:
            status, line = 'err', f"{cid} ({e})"
        (pend['added'] if status == 'added' else pend['warn']).append(line)
    for tok in errors:
        pend['warn'].append(f"{tok} (invalid or bot cannot access it)")
    if pend['timer']:
        pend['timer'].cancel()
    pend['timer'] = threading.Timer(1.2, fc_finalize_add, args=(admin_id,))
    pend['timer'].daemon = True
    pend['timer'].start()
    # keep listening so several forwarded messages can arrive one after another
    bot.register_next_step_handler_by_chat_id(message.chat.id, process_fc_add_channels)

def fc_finalize_add(admin_id):
    pend = fc_pending.pop(admin_id, None)
    if not pend:
        return
    chat_id = pend['chat_id']
    try:
        bot.clear_step_handler_by_chat_id(chat_id)
    except Exception:
        pass
    parts = []
    if pend['added']:
        parts.append("✅ <b>Successfully Added Channels:</b>\n\n" + "\n".join(html.escape(x) for x in pend['added']))
    if pend['warn']:
        parts.append("⚠️ <b>Not Added:</b>\n\n" + "\n".join(html.escape(x) for x in pend['warn']))
    safe_send(chat_id, "\n\n".join(parts) if parts else f"{CE_CROSS} Nothing added.")
    fc_panel(chat_id)

# ---------- social links ----------
SOCIAL_FORMAT_ERROR = ("⚠️ <b>Invalid Format. Please Use:</b>\nName - URL\n"
                       "Example: Twitter - https://twitter.com/yourhandle")

def parse_social(text):
    text = (text or '').strip()
    m = re.match(r'^(.+?)\s+[-–—]\s+(\S+)$', text) or re.match(r'^(.+?)\s*[-–—]\s*((?:https?://|t\.me/)\S+)$', text)
    if not m:
        return None
    name, url = m.group(1).strip(), normalize_url(m.group(2))
    if not name or len(name) > 30 or not valid_url(url):
        return None
    return name, url

def process_fc_social(message, old_url=None):
    if not is_admin_user(message.from_user.id):
        return
    if is_cancel_command(message):
        fc_cancelled(message)
        return
    parsed = parse_social(message.text)
    if not parsed:
        msg = safe_send(message.chat.id, SOCIAL_FORMAT_ERROR)
        if msg:
            bot.register_next_step_handler(msg, process_fc_social, old_url)
        return
    name, url = parsed
    socials = fc_social_links()
    if old_url:
        for s in socials:
            if s['url'] == old_url:
                s['name'], s['url'] = name, url
                break
        verb = "Updated"
    else:
        socials.append({"name": name, "url": url})
        verb = "Added"
    save_settings(BOT_SETTINGS)
    safe_send(message.chat.id, f"✅ <b>Social Link {verb}:</b> {html.escape(name)} - {html.escape(url)}")
    fc_panel(message.chat.id)

# ---------- invite link for a private channel ----------
def process_fc_set_link(message, ch_id):
    if not is_admin_user(message.from_user.id):
        return
    if is_cancel_command(message):
        fc_cancelled(message)
        return
    link = normalize_url(message.text or '')
    if not valid_tg_link(link):
        msg = safe_send(message.chat.id, f"{CE_CROSS} Invalid link. Send a Telegram invite link like <code>https://t.me/+AbCdEf</code>\n<i>/cancel to abort.</i>")
        if msg:
            bot.register_next_step_handler(msg, process_fc_set_link, ch_id)
        return
    for ch in FORCE_CHANNELS:
        if str(ch['id']) == str(ch_id):
            ch['link'] = link
            save_force_channels(FORCE_CHANNELS)
            break
    safe_send(message.chat.id, f"✅ <b>Invite link For {html.escape(str(ch_id))} Updated Successfully!</b>\n\n🔗 <b>New Link:</b> {html.escape(link)}")
    fc_panel(message.chat.id)

# ---------- payout channel / new user channel ----------
def process_fc_single_channel(message, key, label):
    if not is_admin_user(message.from_user.id):
        return
    if is_cancel_command(message):
        fc_cancelled(message)
        return
    if (message.text or '').strip().lower() == '/remove':
        BOT_SETTINGS.pop(key, None)
        save_settings(BOT_SETTINGS)
        safe_send(message.chat.id, f"✅ {label} Removed.")
        fc_panel(message.chat.id)
        return
    chats, errors = extract_chats(message)
    if not chats:
        msg = safe_send(message.chat.id, f"{CE_CROSS} Could not detect the channel. Send @username / Chat ID or forward a message from it.\n<i>/cancel to abort.</i>")
        if msg:
            bot.register_next_step_handler(msg, process_fc_single_channel, key, label)
        return
    chat = chats[0]
    name = getattr(chat, 'title', None) or getattr(chat, 'username', None) or str(chat.id)
    BOT_SETTINGS[key] = {"id": str(chat.id), "name": name}
    save_settings(BOT_SETTINGS)
    warn = "" if bot_is_admin_in(chat.id) else "\n⚠️ Bot is not admin there, it cannot post until you make it admin."
    safe_send(message.chat.id, f"✅ <b>{label} Set:</b> {html.escape(name)} (<code>{chat.id}</code>){warn}")
    fc_panel(message.chat.id)

# ---------- broadcast to all force channels ----------
def process_fc_broadcast(message):
    if not is_admin_user(message.from_user.id):
        return
    if is_cancel_command(message):
        fc_cancelled(message)
        return
    if not FORCE_CHANNELS:
        safe_send(message.chat.id, f"{CE_CROSS} No channels added yet.")
        return
    failed = []
    for ch in FORCE_CHANNELS:
        try:
            bot.copy_message(chat_key(ch['id']), message.chat.id, message.message_id)
        except Exception as e:
            failed.append(f"{ch['id']} ({e})")
        time.sleep(0.1)
    if failed:
        safe_send(message.chat.id, "⚠️ <b>Broadcast sent, but failed in:</b>\n" + "\n".join(html.escape(x) for x in failed))
    else:
        safe_send(message.chat.id, "✅ <b>Broadcast Sent To All Channels Successfully.</b>")
    fc_panel(message.chat.id)

# ---------- callbacks ----------
@bot.callback_query_handler(func=lambda call: call.data == "manage_force_channels" or call.data.startswith("fc_"))
def fc_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    data, chat_id, msg_id = call.data, call.message.chat.id, call.message.message_id

    if data in ("manage_force_channels", "fc_back"):
        try: bot.clear_step_handler_by_chat_id(chat_id)
        except Exception: pass
        safe_callback(call.id)
        fc_panel(chat_id, msg_id)
        return

    if data == "fc_add_ch":
        safe_callback(call.id)
        msg = safe_send(chat_id, "💡 <b>Send Username/Chat ID Of Channel (Username with @), Or Forward Messages From Multiple Channels</b>\n\n<i>Send /cancel to abort.</i>")
        if msg: bot.register_next_step_handler(msg, process_fc_add_channels)
        return

    if data == "fc_add_social":
        safe_callback(call.id)
        msg = safe_send(chat_id, "💡 <b>Send Your Social Link Name and URL</b>\n⚠️ <b>Use Format:</b> Name - URL\n\n👉 <b>Example:</b> Instagram - https://instagram.com/yourprofile")
        if msg: bot.register_next_step_handler(msg, process_fc_social, None)
        return

    if data in ("fc_add_payout", "fc_newuser"):
        key, label = ("payout_channel", "Payout Channel") if data == "fc_add_payout" else ("newuser_channel", "New User Join Channel")
        cur = BOT_SETTINGS.get(key)
        cur_text = f"\n\nCurrent: <b>{html.escape(cur['name'])}</b> (<code>{cur['id']}</code>)\nSend /remove to remove it." if cur else ""
        what = ("Premium payment approvals are posted there." if key == "payout_channel"
                else "A message is posted there whenever a new user starts the bot.")
        safe_callback(call.id)
        msg = safe_send(chat_id, f"💡 <b>Send Username/Chat ID Of {label} (Username with @), Or Forward A Message From It</b>\n\n<i>{what}</i>{cur_text}\n\n<i>Send /cancel to abort.</i>")
        if msg: bot.register_next_step_handler(msg, process_fc_single_channel, key, label)
        return

    if data == "fc_broadcast":
        safe_callback(call.id)
        markup = types.InlineKeyboardMarkup()
        markup.add(CustomInlineKeyboardButton("Back", callback_data="fc_back", style="danger"))
        msg = safe_send(chat_id, "📢 <b>Send A Message To Broadcast In Channels:</b>", reply_markup=markup)
        if msg: bot.register_next_step_handler(msg, process_fc_broadcast)
        return

    if data == "fc_mode":
        BOT_SETTINGS['force_show_mode'] = 'unjoined' if fc_show_mode() == 'all' else 'all'
        save_settings(BOT_SETTINGS)
        safe_callback(call.id, "Show mode: " + ("All Channels" if fc_show_mode() == 'all' else "Not Joined Only"))
        fc_panel(chat_id, msg_id)
        return

    if data.startswith("fc_quick_"):   # from the "Bot Is Admin In" notice
        try:
            chat = bot.get_chat(chat_key(data[len("fc_quick_"):]))
            status, line = add_force_channel_entry(chat)
        except Exception as e:
            safe_callback(call.id, f"Failed: {e}", True)
            return
        safe_callback(call.id, "Added!" if status == 'added' else "Already added!", True)
        fc_panel(chat_id)
        return

    m = re.match(r'^fc_([cs])_(\d+)_(\w+)$', data)
    if not m:
        safe_callback(call.id)
        return
    kind, idx, act = m.group(1), int(m.group(2)), m.group(3)
    items = FORCE_CHANNELS if kind == 'c' else fc_social_links()
    if idx >= len(items):
        safe_callback(call.id, "Item not found, refreshing...", True)
        fc_panel(chat_id, msg_id)
        return
    item = items[idx]
    save = (lambda: save_force_channels(FORCE_CHANNELS)) if kind == 'c' else (lambda: save_settings(BOT_SETTINGS))

    if act in ("up", "dn"):
        j = idx - 1 if act == "up" else idx + 1
        if 0 <= j < len(items):
            items[idx], items[j] = items[j], items[idx]
            save()
            safe_callback(call.id)
            fc_panel(chat_id, msg_id)
        else:
            safe_callback(call.id, "Already at the " + ("top" if act == "up" else "bottom"))
        return

    if act == "del":
        items.pop(idx)
        save()
        safe_callback(call.id, "Removed!")
        if kind == 'c':
            safe_send(chat_id, f"<code>{html.escape(str(item['id']))}</code> <b>Channel Removed Successfully</b>")
        else:
            safe_send(chat_id, f"{html.escape(item['url'])} ({html.escape(item['name'])})\n<b>Social Link Removed Successfully</b>")
        fc_panel(chat_id, msg_id)
        return

    if act == "info":
        safe_callback(call.id)
        if kind == 'c':
            link = item.get('link') or ("https://t.me/" + item['username'] if item.get('username') else "")
            safe_send(chat_id,
                      f"💡 <b>Channel Info</b>\n\n🆔 <b>Name:</b> {html.escape(str(item.get('name')))}\n"
                      f"🆔 <b>Chat ID/Chat Username:</b> <code>{html.escape(str(item['id']))}</code>\n"
                      f"🔗 <b>Private Chat Link:</b> {html.escape(link) if link else 'Not Set'}")
        else:
            safe_send(chat_id,
                      f"💡 <b>Social Link Info</b>\n\n🆔 <b>Name:</b> {html.escape(item['name'])}\n"
                      f"🔗 <b>Social Link:</b> {html.escape(item['url'])}")
        return

    if act == "link" and kind == 'c':
        safe_callback(call.id)
        msg = safe_send(chat_id, f"💡 <b>Send Invite Link For Channel</b> <code>{html.escape(str(item['id']))}</code>\n\n<i>Send /cancel to abort.</i>")
        if msg: bot.register_next_step_handler(msg, process_fc_set_link, str(item['id']))
        return

    if act == "edit" and kind == 's':
        safe_callback(call.id)
        msg = safe_send(chat_id, "💡 <b>Send New Social Link Name and URL</b>\n⚠️ <b>Use Format:</b> Name - URL\n\n"
                                 f"Current: {html.escape(item['name'])} - {html.escape(item['url'])}")
        if msg: bot.register_next_step_handler(msg, process_fc_social, item['url'])
        return

    safe_callback(call.id)

# ---------- "Bot Is Admin In ..." notice ----------
@bot.my_chat_member_handler()
def on_bot_membership_change(update):
    try:
        chat = update.chat
        if chat.type not in ('channel', 'group', 'supergroup'):
            return
        if update.new_chat_member.status == 'administrator' and update.old_chat_member.status != 'administrator':
            if not is_admin_user(update.from_user.id):
                return
            markup = types.InlineKeyboardMarkup()
            markup.add(CustomInlineKeyboardButton("➕ Add To Force Join", callback_data=f"fc_quick_{chat.id}", style="success"))
            safe_send(update.from_user.id, f"✅ <b>Bot Is Admin In</b> <code>{chat.id}</code>!\n{html.escape(chat.title or '')}", reply_markup=markup)
    except Exception as e:
        print(f"my_chat_member error: {e}")

# ==================== PROFILE / USER INFO / REMOVE PREMIUM / BACKUP / RESTORE ====================
restore_waiting = set()

def is_admin_user(uid):
    return uid in ADMIN_IDS or uid == OWNER_ID

def register_user(user):
    """Remember name/username/join date so profile & user-info can show them."""
    try:
        rec = USERS_DB.setdefault(str(user.id), {})
        changed = False
        name = ((user.first_name or '') + ' ' + (user.last_name or '')).strip()
        uname = user.username or ''
        if rec.get('name') != name:
            rec['name'] = name; changed = True
        if rec.get('username') != uname:
            rec['username'] = uname; changed = True
        if not rec.get('joined'):
            rec['joined'] = datetime.now().isoformat(); changed = True
        if changed:
            save_db(USERS_DB)
    except Exception as e:
        print(f"register_user error: {e}")

def get_plan_info(uid):
    """Returns (is_premium, expiry_text, remaining_text)."""
    if is_user_premium(uid):
        try:
            exp = datetime.fromisoformat(USERS_DB[str(uid)]["premium_expiry"])
            left = exp - datetime.now()
            return True, exp.strftime("%d %b %Y, %I:%M %p"), f"{left.days}d {left.seconds // 3600}h left"
        except Exception:
            return True, "Unknown", ""
    return False, "No active plan", ""

def send_with_photo(chat_id, uid, text):
    try:
        photos = bot.get_user_profile_photos(uid, limit=1)
        if photos.total_count > 0:
            bot.send_photo(chat_id, photos.photos[0][-1].file_id, caption=text, parse_mode='HTML')
            return
    except Exception as e:
        print(f"Profile photo error: {e}")
    safe_send(chat_id, text)

def user_counts(uid):
    scripts = get_user_scripts(uid)
    running = sum(1 for s in scripts if is_script_running(uid, s))
    return scripts, running, get_user_files_count(uid)

# ---------- MY PROFILE ----------
@bot.message_handler(func=lambda message: message.text == 'MY PROFILE' and message.chat.type == 'private')
def my_profile(message):
    user = message.from_user
    user_id = user.id
    if is_user_banned(user_id):
        safe_send(message.chat.id, f"{CE_SKULL} <b>Access Denied:</b> You are banned.")
        return
    if not is_user_joined(user_id):
        send_welcome(message)
        return
    if bot_locked and user_id not in ADMIN_IDS:
        safe_send(message.chat.id, f"{CE_LOCK} Bot is locked. Please try later.")
        return

    register_user(user)
    is_prem, expiry_text, left_text = get_plan_info(user_id)
    scripts, running, total_files = user_counts(user_id)
    full_name = ((user.first_name or '') + ' ' + (user.last_name or '')).strip() or "N/A"
    uname = f"@{user.username}" if user.username else "No Username"
    plan = f"{CE_DIAMOND} Premium" if is_prem else f"{CE_PACKAGE} Normal User"
    expiry_line = f"{expiry_text} ({left_text})" if is_prem and left_text else expiry_text

    text = (
        f"<b>{CE_CROWN} MY PROFILE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{CE_SPARKLE} <b>Name:</b> {html.escape(full_name)}\n"
        f"{CE_PIN} <b>Username:</b> {html.escape(uname)}\n"
        f"{CE_ID} <b>User ID:</b> <code>{user_id}</code>\n\n"
        f"{CE_DIAMOND} <b>Plan:</b> {plan}\n"
        f"{CE_TIMER} <b>Expiry:</b> {html.escape(expiry_line)}\n\n"
        f"{CE_STATS} <b>Scripts:</b> {len(scripts)} | {CE_GREEN} Running: {running}\n"
        f"{CE_PACKAGE} <b>Total Files:</b> {total_files}"
    )
    send_with_photo(message.chat.id, user_id, text)

# ---------- ADMIN: USER INFO ----------
@bot.callback_query_handler(func=lambda call: call.data == "admin_user_info")
def admin_user_info_prompt(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    safe_callback(call.id)
    msg = safe_send(call.message.chat.id, f"<b>{CE_ID} USER INFO</b>\n━━━━━━━━━━━━━━━━━━━━\n\nSend the <code>USER_ID</code>:\n\n<i>Send /cancel to cancel.</i>")
    if msg:
        bot.register_next_step_handler(msg, process_user_info)

def process_user_info(message):
    admin_id = message.from_user.id
    if not is_admin_user(admin_id):
        return
    if is_cancel_command(message):
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return
    target = (message.text or "").strip()
    if not target.isdigit():
        safe_send(message.chat.id, f"{CE_CROSS} Invalid User ID. Must be numeric.")
        return
    uid = int(target)
    rec = USERS_DB.get(str(uid), {})
    if not rec and not os.path.isdir(os.path.join(UPLOAD_DIR, str(uid))):
        safe_send(message.chat.id, f"{CE_CROSS} User <code>{uid}</code> not found in database.")
        return

    name, uname = rec.get('name') or '', rec.get('username') or ''
    try:
        chat = bot.get_chat(uid)
        name = ((chat.first_name or '') + ' ' + (chat.last_name or '')).strip() or name
        uname = chat.username or uname
    except Exception:
        pass

    is_prem, expiry_text, left_text = get_plan_info(uid)
    scripts, running, total_files = user_counts(uid)
    joined = rec.get('joined')
    try:
        joined = datetime.fromisoformat(joined).strftime("%d %b %Y") if joined else "Unknown"
    except Exception:
        joined = "Unknown"
    expiry_line = f"{expiry_text} ({left_text})" if is_prem and left_text else expiry_text

    text = (
        f"<b>{CE_ID} USER DETAILS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{CE_SPARKLE} <b>Name:</b> {html.escape(name or 'N/A')}\n"
        f"{CE_PIN} <b>Username:</b> {html.escape('@' + uname) if uname else 'No Username'}\n"
        f"{CE_ID} <b>User ID:</b> <code>{uid}</code>\n"
        f"{CE_DIAMOND} <b>Status:</b> {'Premium' if is_prem else 'Normal User'}\n"
        f"{CE_TIMER} <b>Expiry:</b> {html.escape(expiry_line)}\n"
        f"{CE_PACKAGE} <b>Total Files:</b> {total_files}\n"
        f"{CE_STATS} <b>Scripts:</b> {len(scripts)} ({CE_GREEN} {running} running / {CE_RED} {len(scripts) - running} stopped)\n"
        f"{CE_SKULL} <b>Banned:</b> {'Yes' if is_user_banned(uid) else 'No'}\n"
        f"{CE_SPARKLE} <b>First Seen:</b> {joined}"
    )
    send_with_photo(message.chat.id, uid, text)

# ---------- ADMIN: REMOVE PREMIUM ----------
@bot.callback_query_handler(func=lambda call: call.data == "admin_remove_premium")
def admin_remove_premium_prompt(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    safe_callback(call.id)
    msg = safe_send(call.message.chat.id, f"<b>{CE_CROSS} REMOVE PREMIUM</b>\n━━━━━━━━━━━━━━━━━━━━\n\nSend the <code>USER_ID</code> whose premium you want to remove:\n\n<i>Send /cancel to cancel.</i>")
    if msg:
        bot.register_next_step_handler(msg, process_remove_premium)

def process_remove_premium(message):
    admin_id = message.from_user.id
    if not is_admin_user(admin_id):
        return
    if is_cancel_command(message):
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return
    target = (message.text or "").strip()
    if not target.isdigit():
        safe_send(message.chat.id, f"{CE_CROSS} Invalid User ID. Must be numeric.")
        return
    if not is_user_premium(int(target)):
        safe_send(message.chat.id, f"{CE_WARN} User <code>{target}</code> does not have an active premium plan.")
        return
    USERS_DB[str(int(target))]["premium_expiry"] = None
    save_db(USERS_DB)
    safe_send(message.chat.id, f"{CE_CHECK} Premium removed from <code>{target}</code>. User is now a Normal user.")
    try:
        safe_send(int(target), f"<b>{CE_WARN} PREMIUM REMOVED</b>\n━━━━━━━━━━━━━━━━━━━━\n\nYour Premium membership has been removed by admin.")
    except Exception:
        pass

# ---------- ADMIN: BACKUP ----------
@bot.callback_query_handler(func=lambda call: call.data == "admin_backup")
def admin_backup_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    safe_callback(call.id, "Creating backup...")
    chat_id = call.message.chat.id
    safe_send(chat_id, f"{CE_TIMER} Creating server backup, please wait...")
    def _do():
        if send_backup_to(chat_id, f"Server Backup - {datetime.now().strftime('%d %b %Y %I:%M %p')}\nScripts + users/plans/codes/settings data."):
            safe_send(chat_id, f"{CE_CHECK} Backup sent. Use RESTORE to restore from this file.")
    threading.Thread(target=_do, daemon=True).start()

# ---------- ADMIN: RESTORE ----------
@bot.callback_query_handler(func=lambda call: call.data == "admin_restore")
def admin_restore_prompt(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    safe_callback(call.id)
    restore_waiting.add(call.from_user.id)
    safe_send(
        call.message.chat.id,
        f"<b>{CE_WARN} RESTORE BACKUP</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send the backup <code>.zip</code> file now (the manual backup or the automatic 2-hour backup file).\n\n"
        f"{CE_WARN} Same-name files will be overwritten and all running scripts will be stopped.\n"
        "Max size: 20MB (Telegram bot download limit).\n\n"
        "<i>Send /cancel to cancel.</i>"
    )

@bot.message_handler(commands=['cancel'], func=lambda m: m.from_user.id in restore_waiting)
def cancel_restore(message):
    restore_waiting.discard(message.from_user.id)
    safe_send(message.chat.id, f"{CE_CROSS} Restore cancelled.")

def reload_all_data():
    USERS_DB.clear(); USERS_DB.update(load_db())
    PLANS[:] = load_plans()
    REDEEM_CODES.clear(); REDEEM_CODES.update(load_redeem_codes())
    BANNED_USERS[:] = load_banned_users()
    FORCE_CHANNELS[:] = load_force_channels()
    BOT_SETTINGS.clear(); BOT_SETTINGS.update(load_settings())

def restore_from_zip(zip_path):
    restored_files, restored_data = 0, 0
    with zipfile.ZipFile(zip_path) as z:
        names = [i.filename.replace('\\', '/') for i in z.infolist() if not i.is_dir()]
        new_format = any(n.startswith('user_scripts/') or n.startswith('data/') for n in names)

        for key in list(running_scripts.keys()):
            try:
                uid, sname = key.split('_', 1)
                stop_script(int(uid), sname)
            except Exception:
                pass

        upload_base = os.path.normpath(UPLOAD_DIR)
        for info in z.infolist():
            if info.is_dir():
                continue
            name = info.filename.replace('\\', '/')
            if name == 'backup_info.json' or name.endswith('.pid'):
                continue
            is_data = False
            if new_format:
                if name.startswith('data/'):
                    rel = name[len('data/'):]
                    if rel not in BACKUP_DATA_FILES:
                        continue
                    base, is_data = os.getcwd(), True
                elif name.startswith('user_scripts/'):
                    rel, base = name[len('user_scripts/'):], upload_base
                else:
                    continue
            else:
                rel, base = name, upload_base   # old format: <uid>/<file>
                if not rel.split('/')[0].isdigit():
                    continue
            dest = os.path.normpath(os.path.join(base, rel))
            if not dest.startswith(os.path.normpath(base) + os.sep):
                continue  # zip-slip protection
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with z.open(info) as s, open(dest, 'wb') as out:
                shutil.copyfileobj(s, out)
            if is_data: restored_data += 1
            else: restored_files += 1
    reload_all_data()
    return restored_files, restored_data

@bot.message_handler(content_types=['document'], func=lambda m: m.from_user.id in restore_waiting and m.chat.type == 'private')
def handle_restore_file(message):
    uid = message.from_user.id
    if not is_admin_user(uid):
        restore_waiting.discard(uid)
        return
    doc = message.document
    if not (doc.file_name or '').lower().endswith('.zip'):
        safe_send(message.chat.id, f"{CE_CROSS} Please send a <code>.zip</code> backup file (or /cancel).")
        return
    if doc.file_size and doc.file_size > 20 * 1024 * 1024:
        restore_waiting.discard(uid)
        safe_send(message.chat.id, f"{CE_CROSS} File is over 20MB, Telegram bots cannot download it. Restore manually on the server.")
        return
    restore_waiting.discard(uid)
    safe_send(message.chat.id, f"{CE_TIMER} Restoring backup, please wait...")
    tmp_path = os.path.join(tempfile.gettempdir(), f"restore_{uuid.uuid4().hex}.zip")
    try:
        info = bot.get_file(doc.file_id)
        with open(tmp_path, 'wb') as f:
            f.write(bot.download_file(info.file_path))
        if not zipfile.is_zipfile(tmp_path):
            raise ValueError("Not a valid zip file")
        files_n, data_n = restore_from_zip(tmp_path)
        safe_send(
            message.chat.id,
            f"<b>{CE_CHECK} RESTORE COMPLETE</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            f" ├ Script files restored: <b>{files_n}</b>\n"
            f" ├ Data files restored: <b>{data_n}</b>\n"
            f" └ Users in DB: <b>{len(USERS_DB)}</b>\n\n"
            "<i>All scripts were stopped. Users can start them again from MY SCRIPTS.</i>"
        )
    except Exception as e:
        safe_send(message.chat.id, f"{CE_CROSS} Restore failed: {html.escape(str(e))}")
    finally:
        if os.path.exists(tmp_path):
            try: os.remove(tmp_path)
            except: pass

# ==================== FILE UPLOAD ====================
@bot.message_handler(func=lambda message: message.text == 'UPLOAD FILE' and message.chat.type == 'private')
def upload_prompt(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        safe_send(message.chat.id, f"{CE_SKULL} <b>Access Denied:</b> You are banned.")
        return
    if not is_user_joined(user_id):
        send_welcome(message)
        return
    if bot_locked and user_id not in ADMIN_IDS:
        safe_send(message.chat.id, f"{CE_LOCK} Bot is locked. Please try later.")
        return
    
    if not is_user_premium(user_id):
        existing_scripts = get_user_scripts(user_id)
        if len(existing_scripts) >= 1:
            safe_send(
                message.chat.id,
                f"{CE_WARN} <b>LIMIT REACHED!</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"
                "Normal users can only host **1 script/file** at a time.\n"
                "Upgrade to **Premium** via Buy Premium or Redeem Code!\n\n"
                "<i>Click 'REDEEM CODE' in the main menu to redeem a code.</i>"
            )
            return

    safe_send(
        message.chat.id,
        f"<b>{CE_PACKAGE} UPLOAD WORKSPACE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Please send your script or archive file directly here.\n\n"
        f"<b>{CE_CHECK} Supported formats:</b>\n"
        " ├ <code>.py</code>  (Python)\n"
        " ├ <code>.js</code>  (Node.js)\n"
        " └ <code>.zip</code> (Auto-extractable Archive)\n\n"
        f"{CE_WARN} <b>Max upload size:</b> 20MB"
    )

@bot.message_handler(content_types=['document'])
def handle_upload(message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    if is_user_banned(user_id):
        return
    if not is_user_joined(user_id):
        send_welcome(message)
        return
    if bot_locked and user_id not in ADMIN_IDS:
        safe_send(message.chat.id, f"{CE_LOCK} Bot is locked. Please try later.")
        return
    
    if not is_user_premium(user_id):
        existing_scripts = get_user_scripts(user_id)
        if len(existing_scripts) >= 1:
            safe_send(message.chat.id, f"{CE_WARN} Normal users can only have 1 script. Upgrade to Premium to upload more!")
            return

    doc = message.document
    file_name = doc.file_name
    
    if not any(file_name.endswith(ext) for ext in ['.py', '.js', '.zip']):
        safe_send(message.chat.id, f"{CE_CROSS} Only .py, .js, or .zip files are allowed!")
        return
    
    if doc.file_size > 20 * 1024 * 1024:
        safe_send(message.chat.id, f"{CE_CROSS} File too large! Max size is 20MB.")
        return
    
    status_msg = safe_send(message.chat.id, f"{CE_TIMER} Downloading <code>{file_name}</code>...")
    if not status_msg: return
    
    try:
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file_name)

        with open(file_path, 'wb') as f:
            f.write(downloaded)

        short_id = str(uuid.uuid4())[:8]

        pending_files[short_id] = {
            "user_id": user_id,
            "file_name": file_name,
            "file_path": file_path,
            "file_id": message.document.file_id
        }

        safe_edit(
            message.chat.id, status_msg.message_id,
            f"{CE_TIMER} File <code>{file_name}</code> is under detection.\nOnce approved, you will be notified."
        )

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            CustomInlineKeyboardButton("Approve", callback_data=f"approve_{short_id}", style="success", icon_custom_emoji_id="6030437742066798869"),
            CustomInlineKeyboardButton("Reject", callback_data=f"reject_{short_id}", style="danger", icon_custom_emoji_id="6030331836763213973")
        )

        # Send approval notification to Admin Chat(s)
        for admin_id in ADMIN_IDS:
            admin_msg = bot.send_document(
                admin_id,
                message.document.file_id,
                caption=f"New file request\nUser: {user_id}\nFile: {file_name}",
                reply_markup=markup
            )
            pending_files[short_id][f"admin_msg_id_{admin_id}"] = admin_msg.message_id

        if OWNER_ID not in ADMIN_IDS:
            admin_msg = bot.send_document(
                OWNER_ID,
                message.document.file_id,
                caption=f"New file request\nUser: {user_id}\nFile: {file_name}",
                reply_markup=markup
            )
            pending_files[short_id][f"admin_msg_id_{OWNER_ID}"] = admin_msg.message_id

        # Send approval notification to Admin Upload Channel as well
        upload_ch = BOT_SETTINGS.get("upload_channel")
        if upload_ch:
            try:
                ch_msg = bot.send_document(
                    upload_ch,
                    message.document.file_id,
                    caption=f"<b>New File Pending Approval</b>\nUser: <code>{user_id}</code>\nFile: <code>{file_name}</code>",
                    reply_markup=markup,
                    parse_mode="HTML"
                )
                pending_files[short_id]["admin_msg_id_channel"] = ch_msg.message_id
            except Exception as e:
                print(f"Failed to send approval to upload channel: {e}")

    except Exception as e:
        safe_edit(message.chat.id, status_msg.message_id, f"{CE_CROSS} Error: {str(e)}")

# ==================== APPROVE FILE BUTTON ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_"))
def approve_file(call):
    if call.data.startswith("approve_pay_"):
        return

    short_id = call.data.split("_")[1]
    if short_id not in pending_files:
        safe_callback(call.id, "File expired or not found!", True)
        return

    data = pending_files[short_id]
    user_id = data["user_id"]
    file_name = data["file_name"]
    temp_path = data["file_path"]

    if file_name.endswith('.py'):
        is_valid, error = validate_script(temp_path)
        if not is_valid:
            safe_send(user_id, f"{CE_CROSS} Syntax Error:\n{error}")
            os.remove(temp_path)
            del pending_files[short_id]
            safe_callback(call.id, "Invalid script!", True)
            return

    user_dir = get_user_dir(user_id)
    final_path = os.path.join(user_dir, file_name)

    if file_name.endswith('.zip'):
        try:
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                for name in zip_ref.namelist():
                    if '..' in name or name.startswith('/'):
                        raise Exception("Invalid ZIP structure")
                
                extract_folder = user_dir
                zip_ref.extractall(extract_folder)
                
                main_script = None
                for ext in ['.py', '.js']:
                    if os.path.exists(os.path.join(extract_folder, f"main{ext}")):
                        main_script = f"main{ext}"
                        break
                    if os.path.exists(os.path.join(extract_folder, f"index{ext}")):
                        main_script = f"index{ext}"
                        break
                    if os.path.exists(os.path.join(extract_folder, f"app{ext}")):
                        main_script = f"app{ext}"
                        break
                
                if main_script:
                    safe_send(user_id, f"{CE_CHECK} Extracted ZIP. Found <code>{main_script}</code> as entry point.")
                else:
                    safe_send(user_id, f"{CE_WARN} Extracted ZIP, but could not auto-detect main script.")

        except Exception as e:
            safe_send(user_id, f"{CE_CROSS} Failed to extract ZIP: {e}")
            os.remove(temp_path)
            del pending_files[short_id]
            safe_callback(call.id, "ZIP failure!", True)
            return
            
        os.remove(temp_path)
    else:
        shutil.move(temp_path, final_path)

    temp_dir = os.path.dirname(temp_path)
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    # Clear markup from all admin chats/channels where notification was sent
    for key, msg_id in data.items():
        if key.startswith("admin_msg_id_"):
            if key == "admin_msg_id_channel":
                target_chat = BOT_SETTINGS.get("upload_channel")
            else:
                target_chat = int(key.split("_")[3])
            try:
                bot.edit_message_caption(
                    caption=f"Approved\nUser: {user_id}\nFile: {file_name}",
                    chat_id=target_chat,
                    message_id=msg_id,
                    reply_markup=None
                )
            except Exception:
                pass

    # Send final approved file strictly to the admin's configured UPLOAD CHANNEL
    upload_ch = BOT_SETTINGS.get("upload_channel")
    if upload_ch:
        try:
            with open(final_path, 'rb') as doc_file:
                bot.send_document(
                    upload_ch,
                    doc_file,
                    caption=f"{CE_CHECK} <b>Approved Script Upload</b>\nUser ID: <code>{user_id}</code>\nFile: <code>{file_name}</code>",
                    parse_mode="HTML"
                )
        except Exception as e:
            print(f"Failed to send to upload channel: {e}")

    del pending_files[short_id]
    safe_send(user_id, f"{CE_CHECK} Your file <code>{file_name}</code> is approved!\nNow check MY SCRIPTS.")
    safe_callback(call.id, "Approved")

# ==================== REJECT FILE BUTTON ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_"))
def reject_file(call):
    if call.data.startswith("reject_pay_"):
        return

    short_id = call.data.split("_")[1]
    if short_id not in pending_files:
        safe_callback(call.id, "File not found!", True)
        return

    admin_id = call.from_user.id
    reject_waiting[admin_id] = short_id
    safe_send(admin_id, f"{CE_MAIL} Send rejection reason:")
    safe_callback(call.id)

@bot.message_handler(func=lambda m: m.from_user.id in reject_waiting)
def handle_reject_reason(message):
    admin_id = message.from_user.id
    short_id = reject_waiting[admin_id]

    if is_cancel_command(message):
        safe_send(admin_id, f"{CE_CROSS} Rejection cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        del reject_waiting[admin_id]
        return

    if short_id not in pending_files:
        safe_send(admin_id, f"{CE_CROSS} File not found or expired.")
        del reject_waiting[admin_id]
        return

    reason = message.text
    data = pending_files[short_id]

    user_id = data["user_id"]
    file_name = data["file_name"]
    temp_path = data["file_path"]

    if os.path.exists(temp_path):
        temp_dir = os.path.dirname(temp_path)
        shutil.rmtree(temp_dir, ignore_errors=True)

    for key, msg_id in data.items():
        if key.startswith("admin_msg_id_"):
            if key == "admin_msg_id_channel":
                target_chat = BOT_SETTINGS.get("upload_channel")
            else:
                target_chat = int(key.split("_")[3])
            try:
                bot.edit_message_caption(
                    caption=f"Rejected\nUser: {user_id}\nFile: {file_name}\nReason: {reason}",
                    chat_id=target_chat,
                    message_id=msg_id,
                    reply_markup=None
                )
            except Exception:
                pass

    del pending_files[short_id]
    del reject_waiting[admin_id]

    try:
        safe_send(user_id, f"{CE_CROSS} File <code>{file_name}</code> rejected.\n\n{CE_PIN} <b>Reason:</b>\n{reason}")
    except:
        pass

    safe_send(admin_id, f"{CE_CHECK} Rejection sent successfully.")

# ==================== MY SCRIPTS ====================
@bot.message_handler(func=lambda message: message.text == 'MY SCRIPTS' and message.chat.type == 'private')
def list_scripts(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        safe_send(message.chat.id, f"{CE_SKULL} <b>Access Denied:</b> You are banned.")
        return
    if not is_user_joined(user_id):
        send_welcome(message)
        return
    
    scripts = get_user_scripts(user_id)
    if not scripts:
        safe_send(message.chat.id, f"{CE_PACKAGE} No scripts found.\n\nUse 'UPLOAD FILE' to add scripts.")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for script in sorted(scripts):
        status = "[RUNNING]" if is_script_running(user_id, script) else "[STOPPED]"
        btn_style = "success" if is_script_running(user_id, script) else "primary"
        btn_icon = "6266829404849050968" if is_script_running(user_id, script) else "6030331836763213973"
        markup.add(CustomInlineKeyboardButton(f"{status} {script}", callback_data=f"script_{user_id}_{script}", style=btn_style, icon_custom_emoji_id=btn_icon))
    
    safe_send(
        message.chat.id,
        f"<b>{CE_PACKAGE} YOUR SCRIPTS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Total: <b>{len(scripts)}</b> scripts\n\n"
        f"{CE_GREEN} = <b>Running</b>  |  {CE_RED} = <b>Stopped</b>\n\n"
        "<i>Click on a script to manage it.</i>",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('script_'))
def handle_script_callback(call):
    _, user_id, script_name = call.data.split('_', 2)
    user_id = int(user_id)
    current_user = call.from_user.id
    
    if current_user != user_id and current_user not in ADMIN_IDS:
        safe_callback(call.id, "You can only control your own scripts!", True)
        return
    
    is_running = is_script_running(user_id, script_name)
    safe_callback(call.id)
    
    status_text = f"{CE_GREEN} RUNNING" if is_running else f"{CE_RED} STOPPED"
    
    safe_edit(
        call.message.chat.id, call.message.message_id,
        f"<b>{CE_PACKAGE} SCRIPT CONTROL</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Name:</b> <code>{script_name}</code>\n"
        f"<b>Status:</b> <b>{status_text}</b>\n\n"
        "<i>Choose an action below:</i>",
        reply_markup=script_control_menu(user_id, script_name, is_running)
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('start_'))
def start_script_cmd(call):
    _, user_id, script_name = call.data.split('_', 2)
    user_id = int(user_id)
    
    if call.from_user.id != user_id and call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Permission denied!", True)
        return
    
    user_dir = get_user_dir(user_id)
    script_path = os.path.join(user_dir, script_name)
    
    if not os.path.exists(script_path):
        safe_callback(call.id, "Script not found!", True)
        return
    
    if is_script_running(user_id, script_name):
        safe_callback(call.id, "Script is already running!", True)
        return
    
    safe_callback(call.id, "Starting script...")
    
    if script_name.endswith('.py'):
        threading.Thread(target=run_python_script, args=(script_path, user_id, script_name, call.message.chat.id), daemon=True).start()
    else:
        threading.Thread(target=run_js_script, args=(script_path, user_id, script_name, call.message.chat.id), daemon=True).start()
    
    time.sleep(1)
    fake_msg = call.message
    fake_msg.from_user = call.from_user
    list_scripts(fake_msg)

@bot.callback_query_handler(func=lambda call: call.data.startswith('stop_'))
def stop_script_cmd(call):
    _, user_id, script_name = call.data.split('_', 2)
    user_id = int(user_id)
    
    if call.from_user.id != user_id and call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Permission denied!", True)
        return
    
    if stop_script(user_id, script_name):
        safe_callback(call.id, "Script stopped!")
    else:
        safe_callback(call.id, "Script was not running!", True)
    
    time.sleep(0.5)
    fake_msg = call.message
    fake_msg.from_user = call.from_user
    list_scripts(fake_msg)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_script_cmd(call):
    _, user_id, script_name = call.data.split('_', 2)
    user_id = int(user_id)
    
    if call.from_user.id != user_id and call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Permission denied!", True)
        return
    
    delete_user_script(user_id, script_name)
    safe_callback(call.id, f"Deleted: {script_name}")
    safe_send(call.message.chat.id, f"{CE_CHECK} Deleted <code>{script_name}</code>")
    
    time.sleep(0.5)
    fake_msg = call.message
    fake_msg.from_user = call.from_user
    list_scripts(fake_msg)

@bot.callback_query_handler(func=lambda call: call.data.startswith('logs_'))
def view_logs_cmd(call):
    _, user_id, script_name = call.data.split('_', 2)
    user_id = int(user_id)
    
    if call.from_user.id != user_id and call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Permission denied!", True)
        return
    
    user_dir = get_user_dir(user_id)
    log_path = os.path.join(user_dir, script_name.replace('.py', '.log').replace('.js', '.log'))
    
    if not os.path.exists(log_path):
        safe_callback(call.id, "No logs found yet!", True)
        return
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        if not log_content.strip():
            log_content = "(Log is empty)"
        
        if len(log_content) > 4000:
            log_content = "...\n" + log_content[-3500:]
        
        safe_send(call.message.chat.id, f"<b>LOGS for {script_name}:</b>\n\n<pre>{html.escape(log_content)}</pre>")
        safe_callback(call.id)
    except Exception as e:
        safe_send(call.message.chat.id, f"{CE_CROSS} Error: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_scripts')
def back_to_scripts_cmd(call):
    safe_callback(call.id)
    fake_msg = call.message
    fake_msg.from_user = call.from_user
    list_scripts(fake_msg)

# ==================== INSTALL MODULE ====================
@bot.message_handler(func=lambda message: message.text == 'INSTALL MODULE' and message.chat.type == 'private')
def install_module_prompt(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        safe_send(message.chat.id, f"{CE_SKULL} <b>Access Denied:</b> You are banned.")
        return
    if not is_user_joined(user_id):
        send_welcome(message)
        return
    if bot_locked and user_id not in ADMIN_IDS:
        safe_send(message.chat.id, f"{CE_LOCK} Bot is locked. Please try later.")
        return
    
    msg = safe_send(
        message.chat.id,
        f"<b>{CE_PACKAGE} INSTALL MODULE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Send the module name to install.\n\n"
        "<b>Examples:</b>\n"
        " ├ <code>requests</code>\n"
        " ├ <code>pillow</code>\n"
        " ├ <code>numpy</code>\n"
        " └ <code>telebot</code>\n\n"
        "<i>Send /cancel to cancel.</i>"
    )
    if msg:
        bot.register_next_step_handler(msg, process_install_module)

def process_install_module(message):
    if is_cancel_command(message):
        safe_send(message.chat.id, f"{CE_CROSS} Installation cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return
    
    module_name = message.text.strip()
    install_package(module_name, message.chat.id)

# ==================== STATISTICS ====================
@bot.message_handler(func=lambda message: message.text == 'STATS' and message.chat.type == 'private')
def show_stats(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        safe_send(message.chat.id, f"{CE_SKULL} <b>Access Denied:</b> You are banned.")
        return
    if not is_user_joined(user_id):
        send_welcome(message)
        return
    
    scripts = get_user_scripts(user_id)
    running = sum(1 for s in scripts if is_script_running(user_id, s))
    pending = sum(1 for v in pending_files.values() if v['user_id'] == user_id)
    total_files = get_user_files_count(user_id)
    tier = f"{CE_DIAMOND} Premium" if is_user_premium(user_id) else f"{CE_PACKAGE} Normal (1 File Limit)"
    
    stats_text = (
        f"<b>{CE_STATS} STATISTICS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>USER STATISTICS:</b>\n"
        f" ├ Membership: <b>{tier}</b>\n"
        f" ├ Active Scripts: <b>{len(scripts)}</b>\n"
        f" ├ Total Files: <b>{total_files}</b>\n"
        f" ├ Pending Configs: <b>{pending}</b>\n"
        f" ├ {CE_GREEN} Running: <b>{running}</b>\n"
        f" └ {CE_RED} Stopped: <b>{len(scripts) - running}</b>\n\n"
        f"<b>SYSTEM INFO:</b>\n"
        f" ├ Python: <code>{sys.version.split()[0]}</code>\n"
        f" └ Platform: <code>{sys.platform}</code>"
    )
    safe_send(message.chat.id, stats_text)

# ==================== BOT SPEED ====================
@bot.message_handler(func=lambda message: message.text == 'BOT SPEED' and message.chat.type == 'private')
def bot_speed(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        safe_send(message.chat.id, f"{CE_SKULL} <b>Access Denied:</b> You are banned.")
        return
    if not is_user_joined(user_id):
        send_welcome(message)
        return
    
    start = time.time()
    msg = safe_send(message.chat.id, f"{CE_LIGHTNING} Pinging...")
    end = time.time()
    
    latency = round((end - start) * 1000, 2)
    
    speed_text = (
        f"<b>{CE_LIGHTNING} SERVER PERFORMANCE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Response Time:</b> <code>{latency} ms</code>\n"
        f"<b>Status:</b> Online {CE_CHECK}\n\n"
        f"{CE_GREEN} <i>All systems operational.</i>"
    )
    if msg:
        safe_edit(message.chat.id, msg.message_id, speed_text)

# ==================== HELP ====================
@bot.message_handler(func=lambda message: message.text == 'HELP' and message.chat.type == 'private')
def show_help(message):
    user_id = message.from_user.id
    if is_user_banned(user_id):
        safe_send(message.chat.id, f"{CE_SKULL} <b>Access Denied:</b> You are banned.")
        return
    if not is_user_joined(user_id):
        send_welcome(message)
        return
    
    help_text = (
        f"<b>{CE_HELP} HELP & GUIDE</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{CE_PACKAGE} <b>UPLOAD FILE:</b>\n"
        " • Send .py, .js, or .zip files directly.\n"
        " • Normal users can run 1 file.\n"
        " • Premium users can run unlimited files!\n\n"
        f"{CE_STAR} <b>REDEEM CODE:</b>\n"
        " • Enter your redeem code to get instant Premium access.\n\n"
        f"{CE_LIGHTNING} <b>INSTALL MODULE:</b>\n"
        " • Install Python packages (e.g. <code>requests</code>).\n\n"
        "────────────────────────────\n"
        f"{CE_BROADCAST} Support: @AADITYAXOFFICAL"
    )
    safe_send(message.chat.id, help_text)

# ==================== ADMIN PANEL ====================
@bot.message_handler(func=lambda message: message.text in ['ADMIN PANEL', 'SETTINGS & ADMIN'] and message.chat.type == 'private')
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS and message.from_user.id != OWNER_ID:
        safe_send(message.chat.id, f"{CE_CROSS} Admin access required!")
        return
    
    safe_send(
        message.chat.id,
        f"<b>{CE_CROWN} SETTINGS & ADMIN</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome to the control panel Admin!\n\n"
        "<i>Select an administrative task below:</i>",
        reply_markup=admin_panel_menu()
    )

@bot.callback_query_handler(func=lambda call: call.data == "admin_stats")
def admin_stats_callback(call):
    if call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Admin only!", True)
        return
    
    total_users = len(get_all_users())
    total_scripts = sum(len(get_user_scripts(u)) for u in get_all_users())
    total_system_files = get_total_files_system()
    running = len(running_scripts)
    banned_count = len(BANNED_USERS)
    
    stats = (
        f"<b>{CE_STATS} ADMIN BOT STATISTICS</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>USERS:</b>\n"
        f" ├ Total Users: <b>{total_users}</b>\n"
        f" ├ Banned Users: <b>{banned_count}</b>\n"
        f" ├ Total Scripts: <b>{total_scripts}</b>\n"
        f" ├ Total System Files: <b>{total_system_files}</b>\n"
        f" └ Running Scripts: <b>{running}</b>\n\n"
        f"<b>SYSTEM:</b>\n"
        f" ├ Python: <code>{sys.version.split()[0]}</code>\n"
        f" └ Platform: <code>{sys.platform}</code>"
    )
    safe_callback(call.id)
    safe_edit(call.message.chat.id, call.message.message_id, stats, reply_markup=admin_panel_menu())

# ==================== ALL USERS (CSV) / ALL FILES (TXT) / MANAGE FILES ====================
SKIP_DIRS = {'node_modules', '__pycache__', '.git', 'venv', '.venv', 'env'}
admin_file_tokens = {}

def fmt_size(n):
    n = float(n)
    for unit in ('B', 'KB', 'MB', 'GB'):
        if n < 1024 or unit == 'GB':
            return f"{n:.0f} {unit}" if unit == 'B' else f"{n:.1f} {unit}"
        n /= 1024

def collect_all_user_ids():
    ids = set(get_all_users())
    for k in USERS_DB.keys():
        if str(k).isdigit():
            ids.add(int(k))
    return sorted(ids)

def count_files_nocreate(uid):
    base = os.path.join(UPLOAD_DIR, str(uid))
    if not os.path.isdir(base):
        return 0
    n = 0
    for _, _, files in os.walk(base):
        n += len([f for f in files if not f.endswith('.log')])
    return n

def count_scripts_nocreate(uid):
    base = os.path.join(UPLOAD_DIR, str(uid))
    if not os.path.isdir(base):
        return 0, 0
    scripts = [f for f in os.listdir(base) if f.endswith(('.py', '.js'))]
    running = sum(1 for s in scripts if is_script_running(uid, s))
    return len(scripts), running

def list_user_files(uid):
    """All files of a user (relative paths). Returns (files, skipped_dir_names)."""
    base = os.path.join(UPLOAD_DIR, str(uid))
    files, skipped = [], set()
    if not os.path.isdir(base):
        return files, skipped
    for root, dirs, fnames in os.walk(base):
        for d in list(dirs):
            if d in SKIP_DIRS:
                skipped.add(d)
                dirs.remove(d)
        for fn in fnames:
            if fn.endswith(('.pid', '.log', '.pyc')):
                continue
            files.append(os.path.relpath(os.path.join(root, fn), base).replace(os.sep, '/'))
    scripts = sorted([f for f in files if '/' not in f and f.endswith(('.py', '.js'))], key=str.lower)
    others = sorted([f for f in files if f not in scripts], key=str.lower)
    return scripts + others, skipped

def is_root_script(rel):
    return '/' not in rel and rel.endswith(('.py', '.js'))

def lookup_user_record(uid):
    """Fill name/username from Telegram if we do not have them yet. Returns True if DB changed."""
    rec = USERS_DB.get(str(uid), {})
    if rec.get('name') or rec.get('username') or rec.get('lookup_failed'):
        return False
    try:
        ch = bot.get_chat(uid)
        nm = ((ch.first_name or '') + ' ' + (ch.last_name or '')).strip()
        USERS_DB.setdefault(str(uid), {}).update({'name': nm, 'username': ch.username or ''})
    except Exception:
        USERS_DB.setdefault(str(uid), {})['lookup_failed'] = True
    time.sleep(0.05)
    return True

def csv_safe(v):
    v = str(v or '')
    return "'" + v if v[:1] in ('=', '+', '-', '@') else v

def generate_all_users_file(chat_id):
    status = safe_send(chat_id, f"{CE_TIMER} Generating all users file, please wait...")
    path = None
    try:
        ids = collect_all_user_ids()
        if not ids:
            safe_send(chat_id, f"{CE_CROSS} No users found.")
            return
        changed = False
        for uid in ids:
            if lookup_user_record(uid):
                changed = True
        path = os.path.join(tempfile.gettempdir(), f"all_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        prem_count = banned_count = 0
        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(["No", "User ID", "Name", "Username", "Status", "Premium Expiry", "Time Left",
                        "Scripts", "Running", "Total Files", "Banned", "First Seen"])
            for i, uid in enumerate(ids, 1):
                rec = USERS_DB.get(str(uid), {})
                is_prem, expiry_text, left_text = get_plan_info(uid)
                scripts_n, running_n = count_scripts_nocreate(uid)
                banned = is_user_banned(uid)
                prem_count += 1 if is_prem else 0
                banned_count += 1 if banned else 0
                try:
                    joined = datetime.fromisoformat(rec.get('joined')).strftime("%Y-%m-%d") if rec.get('joined') else ""
                except Exception:
                    joined = ""
                w.writerow([
                    i, uid, csv_safe(rec.get('name')), ("@" + rec['username']) if rec.get('username') else "",
                    "Premium" if is_prem else "Normal",
                    expiry_text if is_prem else "-", left_text if is_prem else "-",
                    scripts_n, running_n, count_files_nocreate(uid),
                    "Yes" if banned else "No", joined
                ])
        if changed:
            save_db(USERS_DB)
        caption = (f"All Users Report\nTotal: {len(ids)} | Premium: {prem_count} | "
                   f"Normal: {len(ids) - prem_count} | Banned: {banned_count}\n"
                   "Open with Excel / Google Sheets.")
        with open(path, 'rb') as f:
            bot.send_document(chat_id, f, caption=caption, visible_file_name=os.path.basename(path))
    except Exception as e:
        print(f"All users file error: {e}")
        safe_send(chat_id, f"{CE_CROSS} Failed to generate file: {html.escape(str(e))}")
    finally:
        if status:
            try: bot.delete_message(chat_id, status.message_id)
            except: pass
        if path and os.path.exists(path):
            try: os.remove(path)
            except: pass

@bot.callback_query_handler(func=lambda call: call.data == "all_users")
def all_users_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    safe_callback(call.id, "Generating file...")
    threading.Thread(target=generate_all_users_file, args=(call.message.chat.id,), daemon=True).start()

def generate_all_files_report(chat_id):
    status = safe_send(chat_id, f"{CE_TIMER} Generating all files report, please wait...")
    path = None
    try:
        ids = collect_all_user_ids()
        lines, total_files, users_with_files = [], 0, 0
        for uid in ids:
            files, skipped = list_user_files(uid)
            if not files:
                continue
            users_with_files += 1
            total_files += len(files)
            rec = USERS_DB.get(str(uid), {})
            uname = ("@" + rec['username']) if rec.get('username') else "no username"
            is_prem = is_user_premium(uid)
            lines.append("=" * 60)
            lines.append(f"USER {uid} | {rec.get('name') or 'N/A'} | {uname} | {'Premium' if is_prem else 'Normal'} | {len(files)} files")
            lines.append("=" * 60)
            base = os.path.join(UPLOAD_DIR, str(uid))
            for n, rel in enumerate(files, 1):
                try:
                    st = os.stat(os.path.join(base, rel))
                    size, mtime = fmt_size(st.st_size), datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    size, mtime = "?", "?"
                tag = ""
                if is_root_script(rel):
                    tag = "  [RUNNING]" if is_script_running(uid, rel) else "  [STOPPED]"
                lines.append(f"  {n:>3}. {rel}  ({size}, {mtime}){tag}")
            if skipped:
                lines.append(f"  (skipped folders: {', '.join(sorted(skipped))})")
            lines.append("")
        header = [
            "ALL USERS FILES REPORT",
            f"Generated: {datetime.now().strftime('%d %b %Y %I:%M %p')}",
            f"Users: {len(ids)} | Users with files: {users_with_files} | Total files: {total_files} | Running scripts: {len(running_scripts)}",
            ""
        ]
        path = os.path.join(tempfile.gettempdir(), f"all_files_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(header + (lines if lines else ["No files found."])))
        with open(path, 'rb') as f:
            bot.send_document(chat_id, f, caption=f"All Files Report\nUsers with files: {users_with_files} | Total files: {total_files}",
                              visible_file_name=os.path.basename(path))
    except Exception as e:
        print(f"All files report error: {e}")
        safe_send(chat_id, f"{CE_CROSS} Failed to generate report: {html.escape(str(e))}")
    finally:
        if status:
            try: bot.delete_message(chat_id, status.message_id)
            except: pass
        if path and os.path.exists(path):
            try: os.remove(path)
            except: pass

@bot.callback_query_handler(func=lambda call: call.data == "admin_all_files")
def admin_all_files_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    safe_callback(call.id, "Generating report...")
    threading.Thread(target=generate_all_files_report, args=(call.message.chat.id,), daemon=True).start()

# ---------- MANAGE FILES (enter user id -> list files -> start/stop/logs/download/delete) ----------
@bot.callback_query_handler(func=lambda call: call.data == "manage_files")
def manage_files_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    safe_callback(call.id)
    msg = safe_send(call.message.chat.id, f"<b>{CE_PACKAGE} MANAGE USER FILES</b>\n━━━━━━━━━━━━━━━━━━━━\n\nSend the <code>USER_ID</code> to see and manage all of that user's files:\n\n<i>Send /cancel to cancel.</i>")
    if msg:
        bot.register_next_step_handler(msg, process_manage_files_uid)

def process_manage_files_uid(message):
    if not is_admin_user(message.from_user.id):
        return
    if is_cancel_command(message):
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return
    target = (message.text or "").strip()
    if not target.isdigit():
        safe_send(message.chat.id, f"{CE_CROSS} Invalid User ID. Must be numeric.")
        return
    uid = int(target)
    if not os.path.isdir(os.path.join(UPLOAD_DIR, str(uid))):
        safe_send(message.chat.id, f"{CE_CROSS} User <code>{uid}</code> has no files / not found.")
        return
    show_user_files(message.chat.id, uid, 0)

def show_user_files(chat_id, uid, page=0, msg_id=None):
    files, skipped = list_user_files(uid)
    rec = USERS_DB.get(str(uid), {})
    who = rec.get('name') or ''
    if rec.get('username'):
        who += f" (@{rec['username']})"
    markup = types.InlineKeyboardMarkup(row_width=1)
    if not files:
        text = f"<b>{CE_PACKAGE} FILES OF USER {uid}</b>\n━━━━━━━━━━━━━━━━━━━━\n\nNo files found."
    else:
        PAGE = 10
        pages = (len(files) + PAGE - 1) // PAGE
        page = max(0, min(page, pages - 1))
        if len(admin_file_tokens) > 3000:
            admin_file_tokens.clear()
        for rel in files[page * PAGE:(page + 1) * PAGE]:
            tok = uuid.uuid4().hex[:10]
            admin_file_tokens[tok] = (uid, rel, page)
            if is_root_script(rel):
                running = is_script_running(uid, rel)
                label = ("[RUNNING] " if running else "[STOPPED] ") + rel
                style, icon = ("success", "6266829404849050968") if running else ("primary", "6030331836763213973")
            else:
                label, style, icon = rel, "primary", "6269214795325510848"
            if len(label) > 55:
                label = label[:52] + "..."
            markup.add(CustomInlineKeyboardButton(label, callback_data=f"afv_{tok}", style=style, icon_custom_emoji_id=icon))
        nav = []
        if page > 0:
            nav.append(CustomInlineKeyboardButton("PREV", callback_data=f"afu_{uid}_{page - 1}", style="primary"))
        if page < pages - 1:
            nav.append(CustomInlineKeyboardButton("NEXT", callback_data=f"afu_{uid}_{page + 1}", style="primary"))
        if nav:
            markup.row(*nav)
        running_n = sum(1 for r in files if is_root_script(r) and is_script_running(uid, r))
        text = (
            f"<b>{CE_PACKAGE} FILES OF USER {uid}</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
            + (f"{CE_SPARKLE} {html.escape(who)}\n" if who.strip() else "")
            + f"Total: <b>{len(files)}</b> files | {CE_GREEN} Running: <b>{running_n}</b>\n"
            + f"Page <b>{page + 1}/{pages}</b>\n"
            + (f"<i>Skipped folders: {html.escape(', '.join(sorted(skipped)))}</i>\n" if skipped else "")
            + "\n<i>Tap a file to manage it.</i>"
        )
    markup.add(CustomInlineKeyboardButton("BACK", callback_data="admin_back", style="primary", icon_custom_emoji_id="6264699552041801361"))
    if msg_id:
        safe_edit(chat_id, msg_id, text, reply_markup=markup)
    else:
        safe_send(chat_id, text, reply_markup=markup)

def get_token_file(tok):
    data = admin_file_tokens.get(tok)
    if not data:
        return None
    uid, rel, page = data
    base = os.path.normpath(os.path.join(UPLOAD_DIR, str(uid)))
    path = os.path.normpath(os.path.join(base, rel))
    if not path.startswith(base + os.sep):
        return None
    return uid, rel, page, path

def render_file_detail(call, tok):
    info = get_token_file(tok)
    if not info or not os.path.isfile(info[3]):
        safe_callback(call.id, "File not found or list expired. Open MANAGE FILES again.", True)
        return
    uid, rel, page, path = info
    st = os.stat(path)
    markup = types.InlineKeyboardMarkup(row_width=2)
    status_line = ""
    if is_root_script(rel):
        running = is_script_running(uid, rel)
        status_line = f"<b>Status:</b> {CE_GREEN + ' RUNNING' if running else CE_RED + ' STOPPED'}\n"
        if running:
            markup.add(
                CustomInlineKeyboardButton("STOP", callback_data=f"afx_{tok}", style="danger", icon_custom_emoji_id="6267262260243076354"),
                CustomInlineKeyboardButton("LOGS", callback_data=f"afl_{tok}", style="primary", icon_custom_emoji_id="6030364658903293193"))
        else:
            markup.add(
                CustomInlineKeyboardButton("START", callback_data=f"afs_{tok}", style="success", icon_custom_emoji_id="6266829404849050968"),
                CustomInlineKeyboardButton("LOGS", callback_data=f"afl_{tok}", style="primary", icon_custom_emoji_id="6030364658903293193"))
    markup.add(
        CustomInlineKeyboardButton("DOWNLOAD", callback_data=f"afg_{tok}", style="primary", icon_custom_emoji_id="6269214795325510848"),
        CustomInlineKeyboardButton("DELETE", callback_data=f"afd_{tok}", style="danger", icon_custom_emoji_id="6035142758480482309"))
    markup.add(CustomInlineKeyboardButton("BACK TO FILES", callback_data=f"afu_{uid}_{page}", style="primary", icon_custom_emoji_id="6264699552041801361"))
    text = (
        f"<b>{CE_PACKAGE} FILE CONTROL</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>User:</b> <code>{uid}</code>\n"
        f"<b>File:</b> <code>{html.escape(rel)}</code>\n"
        f"<b>Size:</b> {fmt_size(st.st_size)}\n"
        f"<b>Modified:</b> {datetime.fromtimestamp(st.st_mtime).strftime('%d %b %Y, %I:%M %p')}\n"
        f"{status_line}\n<i>Choose an action:</i>"
    )
    safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('afu_'))
def af_user_list_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    try:
        _, uid, page = call.data.split('_')
        safe_callback(call.id)
        show_user_files(call.message.chat.id, int(uid), int(page), msg_id=call.message.message_id)
    except Exception as e:
        safe_callback(call.id, f"Error: {e}", True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('afv_'))
def af_view_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    safe_callback(call.id)
    render_file_detail(call, call.data[4:])

@bot.callback_query_handler(func=lambda call: call.data.startswith('afs_'))
def af_start_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    tok = call.data[4:]
    info = get_token_file(tok)
    if not info or not os.path.isfile(info[3]) or not is_root_script(info[1]):
        safe_callback(call.id, "Cannot start this file / list expired.", True)
        return
    uid, rel, page, path = info
    if is_script_running(uid, rel):
        safe_callback(call.id, "Already running!", True)
        return
    safe_callback(call.id, "Starting script...")
    runner = run_python_script if rel.endswith('.py') else run_js_script
    threading.Thread(target=runner, args=(path, uid, rel, call.message.chat.id), daemon=True).start()
    time.sleep(1.5)
    render_file_detail(call, tok)

@bot.callback_query_handler(func=lambda call: call.data.startswith('afx_'))
def af_stop_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    tok = call.data[4:]
    info = get_token_file(tok)
    if not info:
        safe_callback(call.id, "List expired. Open MANAGE FILES again.", True)
        return
    uid, rel, page, path = info
    if stop_script(uid, rel):
        safe_callback(call.id, "Script stopped!")
    else:
        safe_callback(call.id, "Script was not running!", True)
    time.sleep(0.5)
    render_file_detail(call, tok)

@bot.callback_query_handler(func=lambda call: call.data.startswith('afl_'))
def af_logs_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    info = get_token_file(call.data[4:])
    if not info or not is_root_script(info[1]):
        safe_callback(call.id, "No logs for this file.", True)
        return
    uid, rel, page, path = info
    log_path = path.replace('.py', '.log').replace('.js', '.log')
    if not os.path.exists(log_path):
        safe_callback(call.id, "No logs found yet!", True)
        return
    try:
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        if not content.strip():
            content = "(Log is empty)"
        if len(content) > 3500:
            content = "...\n" + content[-3500:]
        safe_callback(call.id)
        safe_send(call.message.chat.id, f"<b>LOGS for {html.escape(rel)} (user {uid}):</b>\n\n<pre>{html.escape(content)}</pre>")
    except Exception as e:
        safe_callback(call.id, f"Error: {e}", True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('afg_'))
def af_download_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    info = get_token_file(call.data[4:])
    if not info or not os.path.isfile(info[3]):
        safe_callback(call.id, "File not found or list expired.", True)
        return
    uid, rel, page, path = info
    if os.path.getsize(path) > 49 * 1024 * 1024:
        safe_callback(call.id, "File is larger than 50MB, cannot send.", True)
        return
    safe_callback(call.id, "Sending file...")
    try:
        with open(path, 'rb') as f:
            bot.send_document(call.message.chat.id, f, caption=f"User {uid}: {rel}", visible_file_name=os.path.basename(path))
    except Exception as e:
        safe_send(call.message.chat.id, f"{CE_CROSS} Could not send file: {html.escape(str(e))}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('afd_'))
def af_delete_confirm_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    tok = call.data[4:]
    info = get_token_file(tok)
    if not info:
        safe_callback(call.id, "List expired. Open MANAGE FILES again.", True)
        return
    uid, rel, page, path = info
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        CustomInlineKeyboardButton("YES, DELETE", callback_data=f"afy_{tok}", style="danger", icon_custom_emoji_id="6030437742066798869"),
        CustomInlineKeyboardButton("NO", callback_data=f"afv_{tok}", style="primary", icon_custom_emoji_id="6030331836763213973"))
    safe_callback(call.id)
    safe_edit(call.message.chat.id, call.message.message_id,
              f"<b>{CE_WARN} CONFIRM DELETION</b>\n━━━━━━━━━━━━━━━━━━━━\n\n<b>User:</b> <code>{uid}</code>\n<b>File:</b> <code>{html.escape(rel)}</code>\n\nAre you absolutely sure?",
              reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('afy_'))
def af_delete_yes_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    tok = call.data[4:]
    info = get_token_file(tok)
    if not info:
        safe_callback(call.id, "List expired. Open MANAGE FILES again.", True)
        return
    uid, rel, page, path = info
    try:
        if is_root_script(rel):
            delete_user_script(uid, rel)
        elif os.path.isfile(path):
            os.remove(path)
        safe_callback(call.id, f"Deleted: {rel}", True)
        try:
            safe_send(uid, f"{CE_WARN} Admin has deleted your file: <code>{html.escape(rel)}</code>")
        except Exception:
            pass
    except Exception as e:
        safe_callback(call.id, f"Delete failed: {e}", True)
    admin_file_tokens.pop(tok, None)
    show_user_files(call.message.chat.id, uid, page, msg_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_user_'))
def view_user_scripts_callback(call):
    if call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Admin only!", True)
        return
    
    user_id = int(call.data.split('_')[2])
    scripts = get_user_scripts(user_id)
    
    if not scripts:
        safe_callback(call.id, "No scripts found!", True)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for script in scripts:
        status = "[RUNNING]" if is_script_running(user_id, script) else "[STOPPED]"
        btn_style = "danger"
        btn_icon = "6035142758480482309"
        markup.add(CustomInlineKeyboardButton(f"{status} {script}", callback_data=f"admin_delete_{user_id}_{script}", style=btn_style, icon_custom_emoji_id=btn_icon))
    
    markup.add(CustomInlineKeyboardButton("BACK", callback_data="manage_files", style="primary", icon_custom_emoji_id="6264699552041801361"))
    
    safe_callback(call.id)
    safe_edit(call.message.chat.id, call.message.message_id, f"<b>USER {user_id} SCRIPTS</b>\n━━━━━━━━━━━━━━━━━━━━\n\n<i>Select a script to delete:</i>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_delete_'))
def admin_delete_script_callback(call):
    if call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Admin only!", True)
        return
    
    parts = call.data.split('_')
    user_id = int(parts[2])
    script_name = '_'.join(parts[3:])
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        CustomInlineKeyboardButton("YES", callback_data=f"confirm_delete_{user_id}_{script_name}", style="danger", icon_custom_emoji_id="6030437742066798869"),
        CustomInlineKeyboardButton("NO", callback_data=f"view_user_{user_id}", style="primary", icon_custom_emoji_id="6030331836763213973")
    )
    
    safe_callback(call.id)
    safe_edit(call.message.chat.id, call.message.message_id, f"<b>{CE_WARN} CONFIRM DELETION</b>\n━━━━━━━━━━━━━━━━━━━━\n\n<b>User:</b> <code>{user_id}</code>\n<b>Script:</b> <code>{script_name}</code>\n\nAre you absolutely sure?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_'))
def confirm_delete_script_callback(call):
    if call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Admin only!", True)
        return
    
    parts = call.data.split('_')
    user_id = int(parts[2])
    script_name = '_'.join(parts[3:])
    
    delete_user_script(user_id, script_name)
    safe_callback(call.id, f"Deleted: {script_name}", True)
    
    try:
        safe_send(user_id, f"{CE_WARN} Admin has deleted your script: <code>{script_name}</code>")
    except:
        pass
    
    view_user_scripts_callback(call)

@bot.callback_query_handler(func=lambda call: call.data == "admin_close")
def admin_close_callback(call):
    if call.from_user.id in ADMIN_IDS or call.from_user.id == OWNER_ID:
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

@bot.callback_query_handler(func=lambda call: call.data == "admin_running_scripts")
def admin_running_scripts(call):
    if call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Admin only!", True)
        return
    
    if not running_scripts:
        safe_edit(call.message.chat.id, call.message.message_id, f"<b>{CE_PLAY} RUNNING SCRIPTS</b>\n━━━━━━━━━━━━━━━━━━━━\n\nNo scripts are currently running.", reply_markup=admin_panel_menu())
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    text = f"<b>{CE_PLAY} RUNNING SCRIPTS</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
    for key, data in running_scripts.items():
        parts = key.split('_', 1)
        uid = parts[0]
        sname = parts[1]
        uptime_secs = int((datetime.now() - data['start_time']).total_seconds())
        text += f"<code>{uid}</code> | <code>{sname}</code> | {uptime_secs}s\n"
        markup.add(CustomInlineKeyboardButton(f"Stop: {sname} ({uid})", callback_data=f"stop_{uid}_{sname}", style="danger", icon_custom_emoji_id="6267262260243076354"))
        
    markup.add(CustomInlineKeyboardButton("BACK", callback_data="admin_back", style="primary", icon_custom_emoji_id="6264699552041801361"))
    safe_callback(call.id)
    safe_edit(call.message.chat.id, call.message.message_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_msg_user")
def admin_msg_user_prompt(call):
    if call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Admin only!", True)
        return
    
    safe_callback(call.id)
    msg = safe_send(call.message.chat.id, f"<b>{CE_MAIL} SEND DIRECT MESSAGE</b>\n━━━━━━━━━━━━━━━━━━━━\n\nReply with the <code>USER_ID</code> you want to message.\n\n<i>Send /cancel to cancel.</i>")
    if msg:
        bot.register_next_step_handler(msg, process_msg_user_id)

def process_msg_user_id(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    if is_cancel_command(message):
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return
        
    target_id = message.text.strip()
    if not target_id.isdigit():
        safe_send(message.chat.id, f"{CE_CROSS} Invalid USER_ID. It must be a number.")
        return
        
    msg = safe_send(message.chat.id, f"Sending message to <code>{target_id}</code>.\n\nNow send the message text:\n<i>Send /cancel to cancel.</i>")
    if msg:
        bot.register_next_step_handler(msg, process_msg_user_text, target_id)

def process_msg_user_text(message, target_id):
    if message.from_user.id not in ADMIN_IDS:
        return
    if is_cancel_command(message):
        safe_send(message.chat.id, f"{CE_CROSS} Cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return
        
    try:
        safe_send(int(target_id), f"<b>{CE_MAIL} MESSAGE FROM ADMIN:</b>\n━━━━━━━━━━━━━━━━━━━━\n\n{html.escape(message.text)}")
        safe_send(message.chat.id, f"{CE_CHECK} Message sent successfully to <code>{target_id}</code>.")
    except Exception as e:
        safe_send(message.chat.id, f"{CE_CROSS} Failed to send message: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "admin_back")
def admin_back_callback(call):
    if not is_admin_user(call.from_user.id):
        safe_callback(call.id, "Admin only!", True)
        return
    safe_callback(call.id)
    safe_edit(
        call.message.chat.id, call.message.message_id,
        f"<b>{CE_CROWN} SETTINGS & ADMIN</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome to the control panel Admin!\n\n"
        "<i>Select an administrative task below:</i>",
        reply_markup=admin_panel_menu()
    )

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast")
def broadcast_prompt(call):
    if call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Admin only!", True)
        return
    
    safe_callback(call.id)
    msg = safe_send(call.message.chat.id, f"<b>{CE_BROADCAST} SYSTEM BROADCAST</b>\n━━━━━━━━━━━━━━━━━━━━\n\nSend the message you want to broadcast to all users:\n\n<i>Send /cancel to cancel.</i>")
    if msg:
        bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    if is_cancel_command(message):
        safe_send(message.chat.id, f"{CE_CROSS} Broadcast cancelled.")
        if message.text in MENU_COMMANDS:
            route_menu_command(message)
        return
    
    users = get_all_users()
    sent = 0
    failed = 0
    status_msg = safe_send(message.chat.id, f"{CE_TIMER} Broadcasting to {len(users)} users...")
    
    for user_id in users:
        try:
            safe_send(int(user_id), f"<b>{CE_BROADCAST} SYSTEM ANNOUNCEMENT:</b>\n━━━━━━━━━━━━━━━━━━━━\n\n{html.escape(message.text)}")
            sent += 1
        except:
            failed += 1
        time.sleep(0.1)
    
    if status_msg:
        safe_edit(message.chat.id, status_msg.message_id, f"<b>{CE_CHECK} Broadcast Complete!</b>\n━━━━━━━━━━━━━━━━━━━━\nDelivered: <b>{sent}</b>\nFailed: <b>{failed}</b>")

@bot.callback_query_handler(func=lambda call: call.data == "clean_logs")
def clean_logs_callback(call):
    if call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Admin only!", True)
        return
    
    deleted = 0
    for user_dir in os.listdir(UPLOAD_DIR):
        user_path = os.path.join(UPLOAD_DIR, user_dir)
        if os.path.isdir(user_path):
            for file in os.listdir(user_path):
                if file.endswith('.log'):
                    try:
                        os.remove(os.path.join(user_path, file))
                        deleted += 1
                    except:
                        pass
    
    safe_callback(call.id, f"Cleaned {deleted} log files!", True)
    safe_edit(call.message.chat.id, call.message.message_id, f"<b>{CE_CHECK} LOG CLEANUP REPORT</b>\n━━━━━━━━━━━━━━━━━━━━\n\nCleaned up <b>{deleted}</b> log files.\n\n<i>Returning to admin menu...</i>", reply_markup=admin_panel_menu())

@bot.callback_query_handler(func=lambda call: call.data == "lock_bot")
def lock_bot_callback(call):
    if call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Admin only!", True)
        return
    
    global bot_locked
    bot_locked = True
    safe_callback(call.id, "Bot locked!", True)
    safe_edit(call.message.chat.id, call.message.message_id, f"<b>{CE_LOCK} SYSTEM LOCKED</b>\n━━━━━━━━━━━━━━━━━━━━\n\nNormal operations paused.", reply_markup=admin_panel_menu())

@bot.callback_query_handler(func=lambda call: call.data == "unlock_bot")
def unlock_bot_callback(call):
    if call.from_user.id not in ADMIN_IDS:
        safe_callback(call.id, "Admin only!", True)
        return
    
    global bot_locked
    bot_locked = False
    safe_callback(call.id, "Unlocked!", True)
    safe_edit(call.message.chat.id, call.message.message_id, f"<b>{CE_UNLOCK} SYSTEM UNLOCKED</b>\n━━━━━━━━━━━━━━━━━━━━\n\nOperations resumed normally.", reply_markup=admin_panel_menu())

# ==================== DEFAULT HANDLER ====================
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    if message.chat.type != 'private':
        return
    if is_user_banned(message.from_user.id):
        return
    if not is_user_joined(message.from_user.id):
        send_welcome(message)
        return
    if bot_locked and message.from_user.id not in ADMIN_IDS:
        safe_send(message.chat.id, f"{CE_LOCK} Bot is locked. Please try later.")
        return
    
    safe_send(message.chat.id, f"{CE_HELP} Unknown command. Please use the buttons below.", reply_markup=main_menu(message.from_user.id))

# ==================== CLEANUP ====================
def cleanup():
    print("Shutting down, stopping all scripts...")
    for key in list(running_scripts.keys()):
        try:
            user_id, script_name = key.split('_', 1)
            stop_script(int(user_id), script_name)
        except:
            pass

atexit.register(cleanup)
signal.signal(signal.SIGTERM, lambda s, f: cleanup())

# ==================== MAIN ====================
if __name__ == '__main__':
    print("=" * 60)
    print("SCRIPT HOSTING BOT STARTED")
    print(f"Upload directory: {UPLOAD_DIR}")
    print(f"Owner ID: {OWNER_ID}")
    print(f"Force Channels Loaded: {len(FORCE_CHANNELS)}")
    print(f"Active Premium Plans: {len(PLANS)}")
    print(f"Active Redeem Codes: {len(REDEEM_CODES)}")
    print(f"Banned Users Loaded: {len(BANNED_USERS)}")
    print(f"Current UPI ID: {BOT_SETTINGS.get('upi_id')}")
    print(f"Upload Channel: {BOT_SETTINGS.get('upload_channel')}")
    print("=" * 60)
    
    keep_alive()
    threading.Thread(target=backup_task, daemon=True).start()
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            print(f"Error: {e}")
            print("Reconnecting in 5 seconds...")
            time.sleep(5)