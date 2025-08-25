import os
import time
import requests
import telebot
import threading
from flask import Flask

app = Flask(__name__)

# 🔧 Konfiguracja z Koyeb Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))  # musi być liczba
SEARCH_URLS = os.getenv("SEARCH_URLS", "").split(";")  # linki rozdzielone średnikiem

bot = telebot.TeleBot(BOT_TOKEN)
seen_ids = set()

# Funkcja sprawdzająca Vinted
def check_vinted():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/115.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    for url in SEARCH_URLS:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            try:
                data = res.json()
                items = data.get("items", [])
            except ValueError:
                print(f"Błąd JSON przy URL {url}: {res.text[:200]}")
                items = []

            new_items = [item for item in items if item["id"] not in seen_ids]
            for item in new_items:
                seen_ids.add(item["id"])
                msg = f"🔎 {item['title']}\n💰 {item['price']['amount']} {item['price']['currency']}\n🔗 {item['url']}"
                bot.send_message(CHAT_ID, msg)
        except Exception as e:
            print(f"Błąd przy URL {url}: {e}")

# 🔄 Pętla w tle co 2 minuty
def loop():
    while True:
        check_vinted()
        time.sleep(120)

threading.Thread(target=loop, daemon=True).start()

@app.route("/")
def home():
    return "Bot działa 24/7!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
