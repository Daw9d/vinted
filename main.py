import requests
import time
import telegram
from flask import Flask

# Flask potrzebny żeby Koyeb widział "webservice"
app = Flask(__name__)

# 🔧 KONFIGURACJA
BOT_TOKEN = "8073820431:AAF6m55PBiI1haJPEqnHgVA1L7LDlmtDxVo"
CHAT_ID = "7307787310"
SEARCH_URL = "https://www.vinted.pl/api/v2/catalog/items?search_text=nike+air+force&order=newest_first"

bot = telegram.Bot(token=BOT_TOKEN)
seen_ids = set()

def check_vinted():
    try:
        res = requests.get(SEARCH_URL, headers={"User-Agent": "Mozilla/5.0"})
        items = res.json().get("items", [])
        new_items = [item for item in items if item["id"] not in seen_ids]

        for item in new_items:
            seen_ids.add(item["id"])
            msg = f"👟 {item['title']}\n💰 {item['price']['amount']} {item['price']['currency']}\n🔗 {item['url']}"
            bot.send_message(chat_id=CHAT_ID, text=msg)

    except Exception as e:
        print("Błąd:", e)

@app.route("/")
def home():
    return "Bot działa 24/7!"

# Pętla w tle
import threading
def loop():
    while True:
        check_vinted()
        time.sleep(120)  # sprawdzanie co 2 min
threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
