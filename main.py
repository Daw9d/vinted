import requests
import time
import telegram
from flask import Flask

# Flask potrzebny żeby Koyeb widział "webservice"
app = Flask(__name__)

# 🔧 KONFIGURACJA
BOT_TOKEN = "8073820431:AAF6m55PBiI1haJPEqnHgVA1L7LDlmtDxVo"
CHAT_ID = "7307787310"
SEARCH_URLS = [
    "https://www.vinted.pl/api/v2/catalog/items?search_text=lego+piraci+z+karaib%C3%B3w&brand_ids[]=89162&search_id=25841938583&order=newest_first",
    "https://www.vinted.pl/api/v2/catalog/items?search_text=lego%20pirates%20of%20the%20Caribbean%20&search_id=17821250222&order=newest_first",
    "https://www.vinted.pl/api/v2/catalog/items?search_text=4184%20lego&search_id=17628538338&order=newest_first",
    "https://www.vinted.pl/api/v2/catalog/items?search_text=lego%20jack%20sparrow&search_id=20932423590&order=newest_first"
]


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

