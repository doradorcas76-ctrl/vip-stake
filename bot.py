import os
import hashlib
from datetime import date
import telebot
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Simple in-memory storage (resets on redeploy, suitable for demo)
user_data = {}

def get_code(user_id: int, today: date) -> str:
    """Generate non-financial participation code."""
    raw = f"{user_id}-{today.isoformat()}-stakebot"
    return hashlib.sha256(raw.encode()).hexdigest()[:8].upper()

@bot.message_handler(commands=['start'])
def cmd_start(message):
    uid = message.from_user.id
    today = date.today()
    user_data.setdefault(uid, {'streak': 0, 'last': None})
    user_data[uid]['last'] = today
    code = get_code(uid, today)
    text = (
        f"👋 Hello, {message.from_user.first_name}!\n\n"
        f"Your participation code for {today.isoformat()}:\n"
        f"`{code}`\n\n"
        f"This code is for personal recording only and has no monetary value.\n"
        f"Use /status to view your streak."
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def cmd_status(message):
    uid = message.from_user.id
    today = date.today()
    data = user_data.get(uid, {'streak': 0, 'last': None})
    if data['last']:
        delta = (today - data['last']).days
        if delta == 1:
            data['streak'] += 1
        elif delta > 1:
            data['streak'] = 1
    else:
        data['streak'] = 1
    data['last'] = today
    user_data[uid] = data
    bot.reply_to(message, f"📊 Streak: {data['streak']} day(s)\nLast active: {today.isoformat()}\n\nThis is a personal habit record only.")

@bot.message_handler(commands=['help'])
def cmd_help(message):
    bot.reply_to(message, "Commands:\n/start - Get today's participation code\n/status - View streak\n/help - This message\n\nNo betting, no money, no prizes involved.")

@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.reply_to(message, "Please use /start, /status, or /help.")

if __name__ == '__main__':
    print("StakeBot is running...")
    bot.infinity_polling()
