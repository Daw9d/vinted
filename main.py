import os
import time
import telebot
from flask import Flask
from playwright.sync_api import sync_playwright

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
SEARCH_URLS = os.getenv("SEARCH_URLS", "").split(";")  # linki do Vinted

bot = telebot.TeleBot(BOT_TOKEN)
seen_titles = set()  # unikalne oferty

def check_vinted():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for url in SEARCH_URLS:
            page.goto(url)
            page.wait_for_selector(".feed-grid__item", timeout=10000)
            items = page.query_selector_all(".feed-grid__item")
            for item in items:
                title_elem = item.query_selector(".feed-grid__item-title")
                price_elem = item.query_selector(".feed-grid__item-price")
                link_elem = item.query_selector("a[href]")

                if title_elem and price_elem and link_elem:
                    title = title_elem.inner_text().strip()
                    price = price_elem.inner_text().strip()
                    link = link_elem.get_attribute("href")
                    if title not in seen_titles:
                        seen_titles.add(title)
                        msg = f"🔎 {title}\n💰 {price}\n🔗 https://www.vinted.pl{link}"
                        bot.send_message(CHAT_ID, msg)
        browser.close()

# wysyła wszystko od razu przy starcie
check_vinted()

# pętla co 2 minuty
import threading
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
