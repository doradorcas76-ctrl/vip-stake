import os
import logging
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

# In-memory store (replace with DB later)
users = {}

VIP_TIERS = {
    "bronze": {"min": 100, "reward": 5},
    "silver": {"min": 500, "reward": 10},
    "gold":   {"min": 1000, "reward": 20},
    "platinum": {"min": 5000, "reward": 50},
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.setdefault(user_id, {"stake": 0, "tier": "none"})

    keyboard = [
        [InlineKeyboardButton("💰 Stake Now", callback_data="stake")],
        [InlineKeyboardButton("🏆 My VIP Tier", callback_data="tier")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="bonus")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎰 *Welcome to VIP Stake Bot!*\n\n"
        "Stake, earn rewards & unlock VIP perks right here in Telegram.\n\n"
        "Choose an option below 👇",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = users.setdefault(user_id, {"stake": 0, "tier": "none"})

    if query.data == "stake":
        data["stake"] += 100
        await query.edit_message_text(
            f"💰 You staked 100 tokens!\nTotal stake: *{data['stake']}*",
            parse_mode="Markdown",
        )
    elif query.data == "tier":
        tier = data["tier"]
        await query.edit_message_text(
            f"🏆 Your current VIP tier: *{tier.upper()}*",
            parse_mode="Markdown",
        )
    elif query.data == "bonus":
        await query.edit_message_text(
            "🎁 Daily bonus claimed! +10 tokens added.",
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
