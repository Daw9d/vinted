import os
import time
import requests
import telebot
import threading
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
SEARCH_URLS = os.getenv("SEARCH_URLS", "").split(";")

bot = telebot.TeleBot(BOT_TOKEN)
seen_ids = set()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}

def check_vinted(send_all=False):
    for url in SEARCH_URLS:
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            try:
                data = res.json()
                items = data.get("items", [])
            except ValueError:
                print(f"Błąd JSON przy URL {url}: {res.text[:200]}")
                items = []

            for item in items:
                if send_all or item["id"] not in seen_ids:
                    seen_ids.add(item["id"])
                    msg = f"🔎 {item['title']}\n💰 {item['price']['amount']} {item['price']['currency']}\n🔗 {item['url']}"
                    bot.send_message(CHAT_ID, msg)
        except requests.exceptions.RequestException as e:
            print(f"Błąd HTTP przy URL {url}: {e}")
        except Exception as e:
            print(f"Inny błąd przy URL {url}: {e}")

# 🔹 Test – przy starcie wysyła wszystkie aktualne oferty
check_vinted(send_all=True)

# 🔹 Pętla w tle co 2 minuty sprawdzająca nowe ogłoszenia
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
