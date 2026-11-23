import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # A simple menu compliant with Telegram Ads requirements (no external links)
    await update.message.reply_text(
        "⚽ **Sports Score Bot**\n\n"
        "Use the commands below to check scores:\n"
        "/score - Get a sample live score update\n"
        "/help - Show this message\n\n"
        "Note: This bot provides simulated data for demonstration and does not link to gambling or third-party sites.",
        parse_mode='Markdown'
    )

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Simulated simple function. In a real scenario, you would fetch from an API here.
    # Keeping it simple and self-contained ensures the bot always responds (Ads requirement).
    await update.message.reply_text(
        "🏀 **NBA (Sample)**\n"
        "Lakers 102 - 98 Celtics (Q4 - 02:15)\n\n"
        "⚾ **MLB (Sample)**\n"
        "Yankees 3 - 1 Red Sox (Top 7th)\n\n"
        "⚽ **EPL (Sample)**\n"
        "Arsenal 2 - 2 Liverpool (FT)\n\n"
        "_Data is simulated for demonstration._"
    )

if __name__ == '__main__':
    # Railway uses the PORT environment variable, but for polling, we just need the token.
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("No BOT_TOKEN found in environment variables.")
        
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("score", score))

    # Run the bot (Polling mode works well on Railway for simple bots)
    application.run_polling()
