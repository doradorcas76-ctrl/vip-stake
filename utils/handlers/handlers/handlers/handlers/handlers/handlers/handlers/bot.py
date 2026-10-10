import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler
)
import database as db
from config import BOT_TOKEN
from handlers import start as h_start
from handlers import daily as h_daily
from handlers import tasks as h_tasks
from handlers import invite as h_invite
from handlers import profile as h_profile
from handlers import rewards as h_rewards
from handlers import admin as h_admin

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(app):
    await db.init_db()
    logger.info("Database initialized.")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing in .env")

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # Commands
    app.add_handler(CommandHandler("start", h_start.start))
    app.add_handler(CommandHandler("stats", h_admin.stats_cmd))
    app.add_handler(CommandHandler("give", h_admin.give_cmd))
    app.add_handler(CommandHandler("broadcast", h_admin.broadcast_cmd))

    # Callbacks
    app.add_handler(CallbackQueryHandler(h_start.menu_callback, pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(h_start.about, pattern="^about$"))
    app.add_handler(CallbackQueryHandler(h_start.help_cmd, pattern="^help$"))
    app.add_handler(CallbackQueryHandler(h_daily.daily, pattern="^daily$"))
    app.add_handler(CallbackQueryHandler(h_tasks.tasks_view, pattern="^tasks$"))
    app.add_handler(CallbackQueryHandler(h_tasks.task_open, pattern="^task:"))
    app.add_handler(CallbackQueryHandler(h_tasks.task_verify, pattern="^verify:"))
    app.add_handler(CallbackQueryHandler(h_invite.invite, pattern="^invite$"))
    app.add_handler(CallbackQueryHandler(h_invite.leaderboard, pattern="^leaderboard$"))
    app.add_handler(CallbackQueryHandler(h_profile.profile, pattern="^profile$"))
    app.add_handler(CallbackQueryHandler(h_rewards.rewards_view, pattern="^rewards$"))
    app.add_handler(CallbackQueryHandler(h_rewards.redeem, pattern="^redeem:"))

    logger.info("VIP Stake bot started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
