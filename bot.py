import os
import hashlib
from datetime import datetime, date
import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Simple in-memory storage (use a DB for production)
user_data = {}

def get_participation_code(user_id: int, today: date) -> str:
    """Generate a deterministic, non-financial participation code."""
    raw = f"{user_id}-{today.isoformat()}-stakebot"
    return hashlib.sha256(raw.encode()).hexdigest()[:8].upper()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    today = date.today()

    if user_id not in user_data:
        user_data[user_id] = {'streak': 0, 'last_date': None}

    code = get_participation_code(user_id, today)
    user_data[user_id]['last_date'] = today

    text = (
        f"👋 Welcome, {message.from_user.first_name}!\n\n"
        f"Your participation code for today ({today.isoformat()}):\n"
        f"`{code}`\n\n"
        f"This code is a personal record of your daily engagement. "
        f"It has no monetary value and cannot be exchanged for prizes.\n\n"
        f"Use /status to see your streak, or /help for more info."
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def send_status(message):
    user_id = message.from_user.id
    today = date.today()
    data = user_data.get(user_id, {'streak': 0, 'last_date': None})

    # Update streak if last visit was yesterday
    if data['last_date']:
        delta = (today - data['last_date']).days
        if delta == 1:
            data['streak'] += 1
        elif delta > 1:
            data['streak'] = 1
        elif delta == 0:
            pass  # same day, no change
    else:
        data['streak'] = 1

    data['last_date'] = today
    user_data[user_id] = data

    text = (
        f"📊 Your participation status:\n"
        f"• Current streak: {data['streak']} day(s)\n"
        f"• Last active: {today.isoformat()}\n\n"
        f"This is a personal engagement record. No rewards, prizes, or financial value are involved."
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['help'])
def send_help(message):
    text = (
        "StakeBot is a simple participation tracker.\n\n"
        "Commands:\n"
        "/start — Generate your daily participation code\n"
        "/status — View your engagement streak\n"
        "/help — Show this message\n\n"
        "This bot does not offer betting, gambling, financial products, "
        "or any prizes. It is purely a personal record-keeping tool."
    )
    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "Please use /start, /status, or /help to interact with this bot.")

if __name__ == '__main__':
    print("StakeBot is running...")
    bot.infinity_polling()
