# main.py

import time
import requests
from datetime import datetime
from telegram import Bot
import csv
import os
from threading import Thread
from flask import Flask, send_file

# === CONFIG ===
TELEGRAM_TOKEN = "YOUR_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID"
COINS = ["CFXUSDT", "PYTHUSDT", "JUPUSDT", "ONEUSDT"]
VOLUME_MULTIPLIER = 2.5
DELAY_SECONDS = 15

# === TELEGRAM SETUP ===
bot = Bot(token=TELEGRAM_TOKEN)

# === LOGGING SETUP ===
os.makedirs("log", exist_ok=True)
log_file = "log/alerts.log"
csv_file = "log/alerts.csv"

# === FLASK WEB SERVER ===
app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>SADDAM is Running</h1><p><a href='/log'>View Logs</a></p>"

@app.route("/log")
def show_log():
    try:
        return send_file("log/alerts.log")
    except FileNotFoundError:
        return "Log not found", 404

# === SNIPER STRATEGY ===
def fetch_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        response = requests.get(url)
        data = response.json()
        if "lastPrice" in data and "volume" in data:
            return float(data["lastPrice"]), float(data["volume"])
        else:
            print(f"[⚠️ INVALID DATA] {symbol}: {data}")
            return None
    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")
        return None

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(log_file, "a") as f:
        f.write(full_message + "\n")

def log_csv(coin, price, volume, strategy):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, coin, price, volume, strategy])

def sniper_loop():
    volumes = {}
    while True:
        for coin in COINS:
            result = fetch_data(coin)
            if result:
                price, volume = result
                old_volume = volumes.get(coin, volume)
                if volume > old_volume * VOLUME_MULTIPLIER:
                    strategy = "PUMP_VOLUME"
                    msg = f"🎯 {coin} | ${price} → Volume: {round(volume / old_volume, 2)}x | Strategy: {strategy}"
                    bot.send_message(chat_id=CHAT_ID, text=msg)
                    log_event(msg)
                    log_csv(coin, price, volume, strategy)
                volumes[coin] = volume
        time.sleep(DELAY_SECONDS)

# === STARTUP ===
if __name__ == "__main__":
    Thread(target=sniper_loop).start()
    app.run(host="0.0.0.0", port=3000)
