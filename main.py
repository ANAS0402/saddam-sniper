import requests
import threading
import time
from flask import Flask

# === CONFIGURATION ===
TELEGRAM_TOKEN = '7831896600:AAG7MH7h3McjcG2ZVdkHDddzblxJABohaa0'
TELEGRAM_CHAT_ID = '1873122742'
WATCHLIST = ['CFX', 'PNUT', 'PYTH', 'MBOX', 'BLUR', 'JUP', 'ONE', 'AI', 'HSMTR']
PUMP_THRESHOLD = 2.0      # % price increase
VOLUME_THRESHOLD = 1.5    # x times volume increase
CHECK_INTERVAL = 60       # seconds

# === TELEGRAM ALERT FUNCTION ===
def send_telegram_message(message):
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=payload)
        print('[✅ TELEGRAM STATUS]', response.status_code)
        print('[📩 TELEGRAM RESPONSE]', response.text)
    except Exception as e:
        print('[❌ TELEGRAM ERROR]', str(e))

# === BINANCE API DATA ===
def fetch_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"[❌ API ERROR] {symbol}: {e}")
        return None

# === ANALYSIS LOGIC ===
def analyze_coin(symbol):
    data = fetch_binance_data(f"{symbol}USDT")
    if not data or 'lastPrice' not in data:
        print(f"[⚠️ INVALID DATA] {symbol}USDT: {data}")
        return

    try:
        price_change = float(data['priceChangePercent'])
        volume_change = float(data['quoteVolume']) / float(data['volume']) if float(data['volume']) != 0 else 0

        print(f"[📊 ANALYSIS] {symbol}: PriceChange={price_change:.2f}%, VolumeChange={volume_change:.2f}x")

        if price_change >= PUMP_THRESHOLD and volume_change >= VOLUME_THRESHOLD:
            message = (
                f"🚨 <b>PUMP ALERT</b>\n\n"
                f"<b>Coin:</b> {symbol}USDT\n"
                f"<b>Price Change:</b> {price_change:.2f}%\n"
                f"<b>Volume Spike:</b> {volume_change:.2f}x\n"
                f"<b>Link:</b> https://www.binance.com/en/trade/{symbol}_USDT"
            )
            send_telegram_message(message)
    except Exception as e:
        print(f"[❌ ANALYSIS ERROR] {symbol}: {e}")

# === MAIN SNIPER LOOP ===
def sniper_loop():
    while True:
        for coin in WATCHLIST:
            analyze_coin(coin.upper())
            time.sleep(1)  # Avoid rate limiting
        time.sleep(CHECK_INTERVAL)

# === FLASK SERVER ===
app = Flask(__name__)

@app.route('/')
def home():
    return '🚀 Saddam Sniper Bot is running!'

# === RUN EVERYTHING ===
if __name__ == '__main__':
    # ✅ Send boot confirmation
    send_telegram_message("✅ Saddam Sniper Bot has started and is LIVE!")
    
    # 🧠 Start sniper loop in background
    thread = threading.Thread(target=sniper_loop)
    thread.daemon = True
    thread.start()

    # 🌐 Start Flask web server
    app.run(host='0.0.0.0', port=3000)

    send_telegram_message("Test alert from Saddam sniper bot 💥")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
