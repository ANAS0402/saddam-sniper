from flask import Flask
from telegram import Bot
import os, threading, time, requests
from datetime import datetime

app = Flask(__name__)

# Load Telegram secrets
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("Missing BOT_TOKEN or CHAT_ID")

bot = Bot(token=BOT_TOKEN)

# Your Binance watchlist (USDT pairs)
WATCHLIST = ["CFX", "PNUT", "PYTH", "MBOX", "BLUR", "JUP", "ONE", "AI", "HSMTR"]

# Binance price snapshot for last check
last_prices = {}

# Parameters
INTERVAL_SEC = 15  # how often to check
PUMP_THRESHOLD = 2  # alerts only on real pumps
VOLUME_THRESHOLD = 1.5  # volume must increase by 50%

def fetch_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"
    try:
        r = requests.get(url, timeout=5)
        return r.json()
    except:
        return None

def analyze_coin(symbol):
    data = fetch_data(symbol)
    if not data: return

    price = float(data["lastPrice"])
    vol = float(data["quoteVolume"])
    price_change = float(data["priceChangePercent"])

    # Baseline tracking
    if symbol not in last_prices:
        last_prices[symbol] = {
            "price": price,
            "volume": vol,
            "ts": time.time()
        }
        return

    prev = last_prices[symbol]
    price_diff_pct = ((price - prev["price"]) / prev["price"]) * 100 if prev["price"] > 0 else 0
    vol_ratio = vol / prev["volume"] if prev["volume"] > 0 else 1

    if abs(price_diff_pct) >= PUMP_THRESHOLD or vol_ratio >= VOLUME_THRESHOLD:
        ts = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        alert = (
            f"🎯 SADDAM SIGNAL: {symbol}USDT\n"
            f"💥 Price Δ: {price_diff_pct:.2f}% | Volume x{vol_ratio:.2f}\n"
            f"📈 24h Change: {price_change:.2f}%\n"
            f"⏰ {ts}"
        )
        bot.send_message(chat_id=CHAT_ID, text=alert)
        print(alert)

    # Update snapshot
    last_prices[symbol] = {
        "price": price,
        "volume": vol,
        "ts": time.time()
    }

def sniper_loop():
    while True:
        for coin in WATCHLIST:
            analyze_coin(coin.upper())
        time.sleep(INTERVAL_SEC)

# Start sniper in background
threading.Thread(target=sniper_loop, daemon=True).start()

@app.route('/')
def home():
    return "🧠 SADDAM SNIPER is live."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
