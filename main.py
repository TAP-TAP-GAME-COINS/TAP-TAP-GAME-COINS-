import os
import sqlite3
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

conn = sqlite3.connect("coins.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, coins INTEGER)")
conn.commit()

@app.route("/get_coins")
def get_coins():
    user_id = request.args.get("user_id")
    c.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    coins = row[0] if row else 0
    return jsonify({"coins": coins})

@app.route("/add_coins", methods=["POST"])
def add_coins():
    data = request.get_json()
    user_id = data.get("user_id")
    amount = data.get("amount", 0)
    c.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    if row:
        new_coins = row[0] + amount
        c.execute("UPDATE users SET coins=? WHERE user_id=?", (new_coins, user_id))
    else:
        new_coins = amount
        c.execute("INSERT INTO users (user_id, coins) VALUES (?, ?)", (user_id, new_coins))
    conn.commit()
    return jsonify({"coins": new_coins})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Play Game 🎮", url="https://YOUR-RENDER-URL/game/index.html")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Taba nan don kunna game:", reply_markup=reply_markup)

def run_bot():
    app_telegram = Application.builder().token(TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.run_polling()

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
