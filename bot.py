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

# Simple in-memory store — replace with a DB for production
members = {}

# Loyalty tiers (points-based, non-gambling)
TIERS = {
    "starter":  {"min": 0,    "perk": "Welcome perks"},
    "bronze":   {"min": 100,  "perk": "Bronze badge + 5 daily points"},
    "silver":   {"min": 500,  "perk": "Silver badge + 10 daily points"},
    "gold":     {"min": 1500, "perk": "Gold badge + 20 daily points"},
    "platinum": {"min": 5000, "perk": "Platinum badge + 50 daily points"},
}


def get_tier(points: int) -> str:
    tier = "starter"
    for name, info in TIERS.items():
        if points >= info["min"]:
            tier = name
    return tier


def get_daily(points: int) -> int:
    return {"starter": 5, "bronze": 5, "silver": 10, "gold": 20, "platinum": 50}[get_tier(points)]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    members.setdefault(uid, {"points": 0, "last_checkin": None})

    keyboard = [
        [InlineKeyboardButton("✅ Daily Check-in", callback_data="checkin")],
        [InlineKeyboardButton("🏆 My Tier", callback_data="tier")],
        [InlineKeyboardButton("📊 My Points", callback_data="points")],
        [InlineKeyboardButton("🎁 Perks", callback_data="perks")],
    ]
    await update.message.reply_text(
        "⭐ *Welcome to VIP Stake Bot!*\n\n"
        "Earn loyalty points, unlock VIP tiers, and enjoy exclusive member perks — "
        "all right here in Telegram.\n\n"
        "Choose an option below 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = members.setdefault(uid, {"points": 0, "last_checkin": None})

    if q.data == "checkin":
        now = datetime.utcnow()
        last = data["last_checkin"]
        if last and now - last < timedelta(hours=24):
            wait = timedelta(hours=24) - (now - last)
            hrs, rem = divmod(wait.seconds, 3600)
            mins = rem // 60
            await q.edit_message_text(
                f"⏳ Already checked in today!\nCome back in *{hrs}h {mins}m*.",
                parse_mode="Markdown",
            )
            return

        reward = get_daily(data["points"])
        data["points"] += reward
        data["last_checkin"] = now
        await q.edit_message_text(
            f"🎉 *Check-in complete!*\n\n"
            f"+{reward} points added.\n"
            f"Total: *{data['points']}* points\n"
            f"Tier: *{get_tier(data['points']).upper()}*",
            parse_mode="Markdown",
        )
    elif q.data == "tier":
        tier = get_tier(data["points"])
        await q.edit_message_text(
            f"🏆 Your VIP tier: *{tier.upper()}*\n\n"
            f"Perk: {TIERS[tier]['perk']}",
            parse_mode="Markdown",
        )
    elif q.data == "points":
        await q.edit_message_text(
            f"📊 You currently have *{data['points']}* points.\n"
            f"Next tier at: *{next((t['min'] for t in TIERS.values() if t['min'] > data['points']), 'MAX')}* points.",
            parse_mode="Markdown",
        )
    elif q.data == "perks":
        lines = [f"• *{name.upper()}* ({info['min']}+ pts): {info['perk']}" for name, info in TIERS.items()]
        await q.edit_message_text(
            "🎁 *VIP Perks*\n\n" + "\n".join(lines),
            parse_mode="Markdown",
        )


def main():
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable is missing!")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    logger.info("VIP Stake Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
