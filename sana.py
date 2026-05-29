import time
import random
import os
import asyncio
from datetime import datetime
import pytz
from instagrapi import Client
from threading import Thread
from flask import Flask
import edge_tts

# --- FLASK WEB SERVER (For 24/7 Hosting) ---
app = Flask('')

@app.route('/')
def home():
    return "Sana Bot is Alive and Running 24/7! 🟢"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

# --- CONFIGURATION ---
USERNAME = os.getenv("sana.b0t")
PASSWORD = os.getenv("Rishu9931")
RISHU = "rx"  # <--- Ye line add kar do (agar nahi hai toh)
BOT_NAME = "sana"


OFF_START_HOUR = 0  
OFF_END_HOUR = 4    

last_wish_date = {} 

# --- EXPANDED DATA POOLS ---
EMOTION_RESPONSES = {
    "happy": ["Wow! Yeh sunke bohot khushi hui 🥰✨", "Mera bot wala dil khush ho gaya! 💖🥳", "Khush raho hamesha! 🧿", "Party kab hai phir? 🥂", "I am so happy for you! 🌟"],
    "sad": ["Arre.. rona nahi! Main hoon na 🥺🧸", "Ek pyari si smile karo please ✨💖", "Waqt sab theek kar dega, himmat rakho! 💪", "Dil chota mat karo, main sun rahi hoon 🌸", "Don't be sad, life is beautiful! 🌈"],
    "angry": ["Itna gussa? Thoda paani piyo ji 🧊🤫", "Relax! Breathe in, breathe out... 🧘‍♀️", "Gusse mein aap acche nahi lagte! 😤", "Shanti doston, ladna achi baat nahi! 🙅‍♀️💔", "Take a chill pill! 💊"],
    "love": ["Aww... kitna pyaar hai yahan! 🥰✨", "Nazar na lage kisi ki! 🧿💖", "Ishq wala love! 🌹", "Itni mithas? Sugar ho jayegi sabko! 🍬", "Pyar baanto, khush raho! 💕"]
}

SHAYARI_LIST = [
    "Ishq ne hamein rula diya, jise chaha use bhula diya... 💔",
    "Humne toh sirf dil lagaya tha, tumne toh jaan hi nikaal li! 😊",
    "Tum milo ya na milo ye naseeb ki baat hai, par sukoon bohot milta hai tumhe apna soch kar. ❤️",
    "Zindagi ke safar mein bohot se log milte hain, par har koi tumhari tarah khaas nahi hota. ✨",
    "Hazaaron mehfil hain aur laakhon mele hain, par jahan tum nahi wahan hum akele hain. 🌸",
    "Dil ke rishte kabhi nahi toot-te, bas waqt ke saath gehre ho jaate hain. 🥀",
    "Log kehte hain pyar ek baar hota hai, lekin mujhe toh tumse har roz hota hai. 😍",
    "Meri khamoshi mein bhi tumhara naam chupa hai. 🤫"
]

JOKES_LIST = [
    "Doctor: Aapko kaunsi bimari hai?\nPatient: Har cheez late samajh aati hai.\nDoctor: Theek hai, kal aana.\nPatient: Kal kyun? Aaj bata do! 🤪",
    "Pappu: Mummy, aaj ek ladki ne mujhe 'I love you' bola! 😍\nMummy: Phir kya hua?\nPappu: Phir meri neend khul gayi! 😭😂",
    "Master ji: 'Sukh' aur 'Dukh' mein kya fark hai?\nStudent: Sir, Shaadi ke pehle 'Sukh' aur baad mein 'Dukh'! 🤣",
    "Santa: Yaar, main apni biwi se bohot tang aa gaya hoon.\nBanta: Kyun bhai?\nSanta: Woh har baat par 'Meri maa ne kaha tha' kehti hai! 🙄",
    "Teacher: Sabse zyada 'Current' kahan lagta hai?\nStudent: Sir, Jab bill bharne ki baari aati hai! ⚡💸"
]

ROAST_RESPONSES = [
    "Aww... gussa aa gaya bache ko? Jaakar mummy se shikayat karo! 🤫🔥",
    "Itna gussa sehat ke liye bura hai ji, aur badtameezi toh bilkul nahi! ❌😤",
    "Dimag toh hai nahi, bas chillana aata hai! 🧊👀",
    "Aapki baatein sunke lag raha hai dimag ne chutti le li hai! 🧠🚫",
    "Itna attitude? Google pe download kiya hai kya? 😏",
    "Beta, pehle tameez seekh lo, phir baat karna! 💅",
    "Aapka logic toh mere purane calculator se bhi slow hai! 🧮"
]

VOICE_DEMAND_RESPONSES = [
    "Hnji, suno meri aawaz! Main online hoon ✨",
    "Hlo doston, kya haal chal hain aap sabke? 🥰",
    "Main haazir hoon! Boliye kya sunna hai aapko? 💖",
    "Audio sunne ka mann hai? Toh lo suno phir! 🎙️",
    "Aa gayi meri aawaz? Suno phir dhyan se! 🌸"
]

# --- VOICE GENERATION ---
async def generate_voice_note(text, filename):
    VOICE = "hi-IN-SwaraNeural"
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filename)

def create_voice_file(text, filename):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_voice_note(text, filename))
    loop.close()

def is_bot_sleeping():
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    return OFF_START_HOUR <= now.hour < OFF_END_HOUR

def detect_emotion(text):
    text = text.lower()
    if any(word in text for word in ["khush", "happy", "maza", "good"]): return "happy"
    if any(word in text for word in ["sad", "udas", "rona", "dukhi"]): return "sad"
    if any(word in text for word in ["gussa", "angry", "ladai"]): return "angry"
    if any(word in text for word in ["love", "pyar", "ishq", "pyaar"]): return "love"
    return None

# --- REPLY LOGIC ---
def generate_reply(text, user_name, cl, thread_id):
    text_lower = text.lower()
    
    if "/help" in text_lower:
        return (f"Sana 🤖 Created by {RISHU}\n"
                "━━━━━━━━━━━━━━━\n"
                "📍 /joke | /toss | /shayari\n"
                "📍 /tagall | /everyone 📢\n"
                "📍 /ping ✅\n"
                "🎙️ Voice Note: Bas bolo 'Sana voice sunao'\n"
                "━━━━━━━━━━━━━━━")

    if "/joke" in text_lower: return random.choice(JOKES_LIST)
    if "/shayari" in text_lower: return random.choice(SHAYARI_LIST)
    if "/toss" in text_lower: return f"🪙 Toss Result: {random.choice(['HEADS', 'TAILS'])}!"
    if "/ping" in text_lower: return "Pong! 🏓 Sana is Active! ✅"
    
    if "/tagall" in text_lower or "/everyone" in text_lower:
        try:
            thread_v2 = cl.thread_v2_data(thread_id)
            users = thread_v2.get("users", [])
            mentions = " ".join([f"@{u['username']}" for u in users])
            return f"📢 **Sana Calling Everyone!**\n\n{mentions}"
        except: return "Tagging failed 🥺 (Bot must be Admin)"

    if any(word in text_lower for word in ["pagal", "badtameez", "gadhe", "gadha", "bhoot"]):
        return f"{user_name} ji, " + random.choice(ROAST_RESPONSES)

    emotion = detect_emotion(text_lower)
    if emotion: return f"{user_name} ji, " + random.choice(EMOTION_RESPONSES[emotion])
    
    return random.choice(["Hlo! 👋", "Hnji, boliye! 💖", "Sahi baat hai! 💯", "Hmm.. ✨", "Kuch toh bolo! 🍭", "Sana is here! 👑"])

# --- AUTOMATION (Morning/Night) ---
def handle_auto_features(cl, thread_id):
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    today_str = now.strftime("%Y-%m-%d")
    if thread_id not in last_wish_date: last_wish_date[thread_id] = {"m": None, "n": None}

    if now.hour == 8 and last_wish_date[thread_id]["m"] != today_str:
        cl.direct_send("Good morning family! ☀️ Uth jao sab jaldi, naya din hai ✨🌸", thread_ids=[thread_id])
        last_wish_date[thread_id]["m"] = today_str
    elif now.hour == 23 and last_wish_date[thread_id]["n"] != today_str:
        cl.direct_send("Good night ji! ✨ So jao ab sab log, sapno mein milte hain 😴🌙", thread_ids=[thread_id])
        last_wish_date[thread_id]["n"] = today_str

# --- MAIN LOOP ---
def bot_loop():
    cl = Client()
    try:
        cl.login(sana.b0t, Rishu9931)
        print("Sana is Online! 🟢")
    except Exception as e:
        print(f"Login Error: {e}"); return 

    while True:
        try:
            if is_bot_sleeping(): time.sleep(300); continue
            threads = cl.direct_threads(amount=10)
            for thread in threads:
                thread_id = thread.id
                if thread.is_group: handle_auto_features(cl, thread_id)
                messages = cl.direct_messages(thread_id, amount=1)
                
                if not messages or messages[0].user_id == cl.user_id: continue
                
                msg_text = messages[0].text if messages[0].text else ""
                
                if thread.is_group and messages[0].item_type == 'action_log':
                    if any(x in msg_text.lower() for x in ["added", "joined"]):
                        cl.direct_send("Welcome to our world! 🎉 Pyari si smile ke sath entry karo sab ✨", thread_ids=[thread_id])
                    elif any(x in msg_text.lower() for x in ["left", "removed"]):
                        cl.direct_send("Chalo, ek baddameez kam hua group se! 🏃‍♀️💨 Sukoon mila!", thread_ids=[thread_id])
                    continue

                should_reply = not thread.is_group or (BOT_NAME in msg_text.lower() or msg_text.startswith("/"))
                
                if should_reply:
                    time.sleep(random.randint(4, 7)) 
                    try:
                        user_info = cl.user_info(messages[0].user_id)
                        name = user_info.full_name if user_info.full_name else "Ji"
                    except: name = "Ji"

                    voice_words = ["voice sunao", "voice note do", "apni voice"]
                    is_voice_demanded = any(w in msg_text.lower() for w in voice_words)
                    is_random_voice = random.random() < 0.15 

                    if is_voice_demanded or is_random_voice:
                        reply_text = random.choice(VOICE_DEMAND_RESPONSES) if is_voice_demanded else generate_reply(msg_text, name, cl, thread_id)
                        fname = f"v_{thread_id}.mp3"
                        create_voice_file(reply_text, fname)
                        cl.direct_send_v2_media(fname, media_type=2, thread_ids=[thread_id])
                        if os.path.exists(fname): os.remove(fname)
                    else:
                        cl.direct_send(generate_reply(msg_text, name, cl, thread_id), thread_ids=[thread_id])
            time.sleep(15)
        except: time.sleep(25)

if __name__ == "__main__":
    Thread(target=run_web_server).start()
    bot_loop()
