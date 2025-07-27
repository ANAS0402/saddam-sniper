from flask import Flask
from telegram import Bot
import os
import threading
import time
import requests

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN or CHAT_ID is not set in environment")

bot = Bot(token=BOT_TOKEN)

# === Settings ===
COINS = ["CFX", "PNUT", "PYTH", "MBOX", "BLUR", "JUP", "ONE", "AI", "HSMTR"]
PUMP_THRESHOLD = 2  # % price pump threshold
VOLUME_THRESHOLD = 1.5  # 1.5x volume

previous_prices = {}
previous_volumes = {}

def analyze_coin(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"
    try:
        response = requests.get(url)
        data = response.json()

        if "lastPrice" not in data:
            print(f"[⚠️ INVALID DATA] {symbol}USDT: {data}")
            return

        price = float(data["lastPrice"])
        volume = float(data["quoteVolume"])

        prev_price = previous_prices.get(symbol)
        prev_volume = previous_volumes.get(symbol)

        previous_prices[symbol] = price
        previous_volumes[symbol] = volume

        if prev_price and prev_volume:
            price_change = ((price - prev_price) / prev_price) * 100
            volume_ratio = volume / prev_volume

            if price_change >= PUMP_THRESHOLD and volume_ratio >= VOLUME_THRESHOLD:
                alert_msg = (
                    f"🚨 SADDAM SIGNAL: {symbol}USDT\n"
                    f"📈 Price Pump: {price_change:.2f}%\n"
                    f"🔥 Volume x{volume_ratio:.2f}"
                )
                bot.send_message(chat_id=CHAT_ID, text=alert_msg)
                print(f"[✅ ALERT] {alert_msg}")

    except Exception as e:
        print(f"[❌ ERROR] {symbol}: {e}")

def sniper_loop():
    while True:
        for coin in COINS:
            analyze_coin(coin.upper())
        time.sleep(20)  # Check every 20 seconds

threading.Thread(target=sniper_loop, daemon=True).start()

@app.route("/")
def home():
    return "🟢 SADDAM SNIPER is running!"
    send_telegram_message("Test alert from Saddam sniper bot 💥")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
