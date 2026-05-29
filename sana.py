import time, random, os, asyncio, pytz, threading
from datetime import datetime
from instagrapi import Client
from flask import Flask
import edge_tts
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = "8869794175:AAFVIApu9NeKmTs_3XdNQlvHkRwoDn9PFV4"
OWNER_ID = 7835759934
BOT_NAME = "sana"

# --- FLASK ---
app = Flask('')
@app.route('/')
def home(): return "Sana Bot is Alive! 🟢"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()

# --- DATA POOLS ---
EMOTION_RESPONSES = {"happy": ["Wow! Yeh sunke bohot khushi hui 🥰✨", "Mera bot wala dil khush ho gaya! 💖🥳"], "sad": ["Arre.. rona nahi! Main hoon na 🥺🧸"], "angry": ["Itna gussa? Thoda paani piyo ji 🧊🤫"], "love": ["Aww... kitna pyaar hai yahan! 🥰✨"]}
SHAYARI_LIST = ["Ishq ne hamein rula diya... 💔", "Tum milo ya na milo ye naseeb ki baat hai... ✨"]
JOKES_LIST = ["Doctor: Aapko kaunsi bimari hai? Patient: Har cheez late samajh aati hai. 🤪"]
ROAST_RESPONSES = ["Beta, pehle tameez seekh lo, phir baat karna! 💅"]
VOICE_DEMAND_RESPONSES = ["Hnji, suno meri aawaz! Main online hoon ✨"]

# --- HELPERS ---
async def generate_voice_note(text, filename):
    communicate = edge_tts.Communicate(text, "hi-IN-SwaraNeural")
    await communicate.save(filename)

def create_voice_file(text, filename):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_voice_note(text, filename))
    loop.close()

def detect_emotion(text):
    text = text.lower()
    if any(w in text for w in ["khush", "happy"]): return "happy"
    if any(w in text for w in ["sad", "rona"]): return "sad"
    if any(w in text for w in ["gussa", "angry"]): return "angry"
    if any(w in text for w in ["love", "pyar"]): return "love"
    return None

# --- INSTA LOGIC ---
def bot_loop(username, password):
    cl = Client()
    session_file = f"{username}_session.json"
    if os.path.exists(session_file): cl.load_settings(session_file)
    cl.login(username, password)
    cl.dump_settings(session_file)
    
    while True:
        try:
            threads = cl.direct_threads(amount=5)
            for thread in threads:
                messages = cl.direct_messages(thread.id, amount=1)
                if not messages or messages[0].user_id == cl.user_id: continue
                msg = messages[0].text or ""
                
                # Help & Commands
                if "/help" in msg.lower():
                    reply = "Sana 🤖 Commands: /joke, /shayari, /toss, /ping. Bolo 'Sana voice sunao' for voice!"
                elif "/joke" in msg.lower(): reply = random.choice(JOKES_LIST)
                elif "/shayari" in msg.lower(): reply = random.choice(SHAYARI_LIST)
                elif detect_emotion(msg): reply = random.choice(EMOTION_RESPONSES[detect_emotion(msg)])
                elif any(w in msg.lower() for w in ["pagal", "gadha"]): reply = random.choice(ROAST_RESPONSES)
                elif "voice sunao" in msg.lower():
                    fname = f"v_{thread.id}.mp3"
                    create_voice_file(random.choice(VOICE_DEMAND_RESPONSES), fname)
                    cl.direct_send_v2_media(fname, media_type=2, thread_ids=[thread.id])
                    if os.path.exists(fname): os.remove(fname)
                    continue
                else: reply = "Hnji, boliye! 💖"
                
                cl.direct_send(reply, thread_ids=[thread.id])
            time.sleep(60)
        except: time.sleep(60)

# --- TG COMMAND ---
async def add_insta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if len(context.args) < 2: await update.message.reply_text("Format: /addinsta [user] [pass]"); return
    threading.Thread(target=bot_loop, args=(context.args[0], context.args[1]), daemon=True).start()
    await update.message.reply_text(f"✅ {context.args[0]} active!")

if __name__ == '__main__':
    app_tg = ApplicationBuilder().token(TOKEN).build()
    app_tg.add_handler(CommandHandler("addinsta", add_insta))
    app_tg.run_polling()
                
