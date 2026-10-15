import os
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN")

# Simple in-memory storage
users = {}

# VIP Levels — pure loyalty rewards
LEVELS = {
    "member":   {"min": 0,    "daily": 5,  "perk": "Welcome badge"},
    "bronze":   {"min": 100,  "daily": 10, "perk": "Bronze badge"},
    "silver":   {"min": 500,  "daily": 20, "perk": "Silver badge"},
    "gold":     {"min": 1500, "daily": 35, "perk": "Gold badge"},
    "platinum": {"min": 5000, "daily": 50, "perk": "Platinum badge"},
}


def get_level(points: int) -> str:
    level = "member"
    for name, info in LEVELS.items():
        if points >= info["min"]:
            level = name
    return level


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    users.setdefault(uid, {"points": 0, "last_claim": None})

    keyboard = [
        [InlineKeyboardButton("🎁 Claim Daily Reward", callback_data="claim")],
        [InlineKeyboardButton("⭐ My VIP Level", callback_data="level")],
        [InlineKeyboardButton("📊 My Points", callback_data="points")],
    ]
    await update.message.reply_text(
        "⭐ *Welcome to VIP Rewards Bot!*\n\n"
        "Claim your daily reward, earn points, and unlock VIP levels\n\n"
        "Tap an option below 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = users.setdefault(uid, {"points": 0, "last_claim": None})

    if q.data == "claim":
        now = datetime.utcnow()
        last = data["last_claim"]
        if last and now - last < timedelta(hours=24):
            wait = timedelta(hours=24) - (now - last)
            hrs, rem = divmod(wait.seconds, 3600)
            mins = rem // 60
            await q.edit_message_text(
                f"⏳ Already claimed!\nCome back in *{hrs}h {mins}m*.",
                parse_mode="Markdown",
            )
            return

        reward = LEVELS[get_level(data["points"])]["daily"]
        data["points"] += reward
        data["last_claim"] = now
        await q.edit_message_text(
            f"🎉 *Reward Claimed!*\n\n"
            f"+{reward} points added.\n"
            f"Total: *{data['points']}* points\n"
            f"VIP Level: *{get_level(data['points']).upper()}*",
            parse_mode="Markdown",
        )
    elif q.data == "level":
        level = get_level(data["points"])
        await q.edit_message_text(
            f"⭐ Your VIP Level: *{level.upper()}*\n\n"
            f"Perk: {LEVELS[level]['perk']}",
            parse_mode="Markdown",
        )
    elif q.data == "points":
        nxt = next((l["min"] for l in LEVELS.values() if l["min"] > data["points"]), None)
        nxt_txt = f"Next level at *{nxt}* points." if nxt else "You've reached the top level! 🎉"
        await q.edit_message_text(
            f"📊 You have *{data['points']}* points.\n{nxt_txt}",
            parse_mode="Markdown",
        )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing!")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("VIP Rewards Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
