import os
import json
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# === КАЛИДҲО ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# === ЛУҒАТ ===
WORDS = {
    "саломӣ": [
        {"en": "Hello", "pr": "хэ-ЛОУ", "tj": "Салом"},
        {"en": "Goodbye", "pr": "гуд-БАЙ", "tj": "Хайр"},
        {"en": "Please", "pr": "ПЛИЗ", "tj": "Илтимос"},
        {"en": "Thank you", "pr": "СЭНК ю", "tj": "Раҳмат"},
        {"en": "Sorry", "pr": "СО-ри", "tj": "Мебахшед"},
    ],
    "рангҳо": [
        {"en": "Red", "pr": "РЕД", "tj": "Сурх"},
        {"en": "Blue", "pr": "БЛУ", "tj": "Кабуд"},
        {"en": "Green", "pr": "ГРИН", "tj": "Сабз"},
        {"en": "White", "pr": "ВАЙТ", "tj": "Сафед"},
        {"en": "Black", "pr": "БЛЭК", "tj": "Сиёҳ"},
    ],
    "оила": [
        {"en": "Mother", "pr": "МА-зер", "tj": "Модар"},
        {"en": "Father", "pr": "ФА-зер", "tj": "Падар"},
        {"en": "Brother", "pr": "БРА-зер", "tj": "Бародар"},
        {"en": "Sister", "pr": "СИС-тер", "tj": "Хоҳар"},
        {"en": "Friend", "pr": "ФРЕНД", "tj": "Дӯст"},
    ],
    "феълҳо": [
        {"en": "Go", "pr": "ГОУ", "tj": "Рафтан"},
        {"en": "Come", "pr": "КАМ", "tj": "Омадан"},
        {"en": "Eat", "pr": "ИТ", "tj": "Хӯрдан"},
        {"en": "Sleep", "pr": "СЛИП", "tj": "Хобидан"},
        {"en": "Work", "pr": "ВЕ:РК", "tj": "Кор кардан"},
        {"en": "Study", "pr": "СТА-ди", "tj": "Омӯхтан"},
        {"en": "Love", "pr": "ЛАВ", "tj": "Дӯст доштан"},
    ],
    "таом": [
        {"en": "Water", "pr": "ВО:-тер", "tj": "Об"},
        {"en": "Bread", "pr": "БРЕД", "tj": "Нон"},
        {"en": "Meat", "pr": "МИТ", "tj": "Гӯшт"},
        {"en": "Tea", "pr": "ТИ", "tj": "Чой"},
        {"en": "Milk", "pr": "МИЛК", "tj": "Шир"},
    ],
}

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    requests.post(f"{TELEGRAM_API}/sendMessage", json=data)

def ask_gemini(question):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""Ту омӯзгори забони англисӣ барои тоҷикзабонон ҳастӣ.
Ба забони тоҷикӣ ҷавоб деҳ. Кӯтоҳ ва равшан.
Савол: {question}"""
    
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, json=body, timeout=15)
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Айб! Дубора кӯшиш кун 🙏"

def main_keyboard():
    return {
        "keyboard": [
            [{"text": "📚 Мавзӯъҳо"}, {"text": "🎯 Санҷиш"}],
            [{"text": "❓ Савол диҳ"}, {"text": "ℹ️ Ёрӣ"}]
        ],
        "resize_keyboard": True
    }

def topics_keyboard():
    return {
        "keyboard": [
            [{"text": "👋 Саломӣ"}, {"text": "🎨 Рангҳо"}],
            [{"text": "👨‍👩‍👧 Оила"}, {"text": "⚡ Феълҳо"}],
            [{"text": "🍞 Таом"}, {"text": "🔙 Бозгашт"}]
        ],
        "resize_keyboard": True
    }

def handle_update(update):
    if "message" not in update:
        return
    
    msg = update["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    name = msg["from"].get("first_name", "Дӯст")

    # START
    if text == "/start":
        send_message(chat_id,
            f"Салом, <b>{name}</b>! 🎉\n\n"
            "Ман <b>Забономӯз</b> ҳастам 🤖\n"
            "Ба ту забони англисӣ меомӯзам!\n\n"
            "Чӣ мехоҳӣ?",
            main_keyboard()
        )

    # МАВЗӮЪҲО
    elif text == "📚 Мавзӯъҳо":
        send_message(chat_id, "Мавзӯъро интихоб кун 👇", topics_keyboard())

    # САЛОМӢ
    elif text == "👋 Саломӣ":
        words = WORDS["саломӣ"]
        resp = "👋 <b>Калимаҳои Саломӣ:</b>\n\n"
        for w in words:
            resp += f"🔹 <b>{w['en']}</b> [{w['pr']}] — {w['tj']}\n"
        send_message(chat_id, resp, topics_keyboard())

    # РАНГҲО
    elif text == "🎨 Рангҳо":
        words = WORDS["рангҳо"]
        resp = "🎨 <b>Рангҳо:</b>\n\n"
        for w in words:
            resp += f"🔹 <b>{w['en']}</b> [{w['pr']}] — {w['tj']}\n"
        send_message(chat_id, resp, topics_keyboard())

    # ОИЛА
    elif text == "👨‍👩‍👧 Оила":
        words = WORDS["оила"]
        resp = "👨‍👩‍👧 <b>Оила:</b>\n\n"
        for w in words:
            resp += f"🔹 <b>{w['en']}</b> [{w['pr']}] — {w['tj']}\n"
        send_message(chat_id, resp, topics_keyboard())

    # ФЕЪЛҲО
    elif text == "⚡ Феълҳо":
        words = WORDS["феълҳо"]
        resp = "⚡ <b>Феълҳо:</b>\n\n"
        for w in words:
            resp += f"🔹 <b>{w['en']}</b> [{w['pr']}] — {w['tj']}\n"
        send_message(chat_id, resp, topics_keyboard())

    # ТАОМ
    elif text == "🍞 Таом":
        words = WORDS["таом"]
        resp = "🍞 <b>Таом:</b>\n\n"
        for w in words:
            resp += f"🔹 <b>{w['en']}</b> [{w['pr']}] — {w['tj']}\n"
        send_message(chat_id, resp, topics_keyboard())

    # БОЗГАШТ
    elif text == "🔙 Бозгашт":
        send_message(chat_id, "Асосӣ 👇", main_keyboard())

    # САНҶИШ
    elif text == "🎯 Санҷиш":
        send_message(chat_id,
            "🎯 <b>Санҷиш:</b>\n\n"
            "Ин калима тоҷикӣ чист?\n\n"
            "<b>WATER</b> [ВО:-тер]\n\n"
            "Ҷавоб бинависав 👇",
            {"remove_keyboard": True}
        )

    # ЁРӢ
    elif text == "ℹ️ Ёрӣ":
        send_message(chat_id,
            "ℹ️ <b>Ёрӣ:</b>\n\n"
            "📚 <b>Мавзӯъҳо</b> — калимаҳо бо талаффуз\n"
            "🎯 <b>Санҷиш</b> — худро санҷ\n"
            "❓ <b>Савол диҳ</b> — ҳар чизро бипурс\n\n"
            "Мисол: <i>«Apple чӣ маъно дорад?»</i>",
            main_keyboard()
        )

    # САВОЛ
    elif text == "❓ Савол диҳ":
        send_message(chat_id,
            "❓ Саволи худро бинависав!\n\n"
            "Мисол:\n"
            "• <i>Apple чӣ маъно дорад?</i>\n"
            "• <i>How are you чӣ маъно дорад?</i>\n"
            "• <i>Рӯз бахайр англисӣ чӣ мешавад?</i>",
            {"remove_keyboard": True}
        )

    # САНҶИШ ҶАВОБ
    elif text.lower() in ["об", "ob", "вода"]:
        send_message(chat_id,
            "✅ <b>Дуруст!</b> Офарин!\n\n"
            "WATER = Об 💧",
            main_keyboard()
        )

    # GEMINI — ҲАМА САВОЛҲОИ ДИГАР
    else:
        send_message(chat_id, "⏳ Фикр мекунам...")
        answer = ask_gemini(text)
        send_message(chat_id, f"🤖 {answer}", main_keyboard())


# === SERVER БАРОИ RENDER ===
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            update = json.loads(body)
            threading.Thread(target=handle_update, args=(update,)).start()
        except:
            pass
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Zabonomuz Bot is running! 🚀")

    def log_message(self, *args):
        pass

def set_webhook():
    render_url = os.environ.get("RENDER_URL", "")
    if render_url:
        url = f"{TELEGRAM_API}/setWebhook?url={render_url}/webhook"
        requests.get(url)

if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get("PORT", 8080))
    print(f"✅ Бот кор мекунад! Port: {port}")
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()
