import time
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import database as db
from utils.helpers import can_checkin
from config import POINTS_DAILY
from keyboards import back_menu


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = await db.get_user(user_id)

    if not user:
        await query.edit_message_text("Please send /start first.")
        return

    if not can_checkin(user["last_daily"]):
        remaining = 86400 - (int(time.time()) - user["last_daily"])
        h, m = divmod(remaining // 60, 60)
        await query.edit_message_text(
            f"⏳ You've already checked in today.\n\n"
            f"Come back in <b>{h}h {m}m</b> for your next reward!",
            parse_mode=ParseMode.HTML,
            reply_markup=back_menu(),
        )
        return

    # streak logic: if within 48h, +1 else reset to 1
    streak = user["streak"] + 1 if (int(time.time()) - user["last_daily"]) < 172800 else 1
    bonus = min(streak, 7) * 2
    total = POINTS_DAILY + bonus

    await db.update_points(user_id, total)
    await db.set_last_daily(user_id, int(time.time()), streak)

    await query.edit_message_text(
        f"✅ <b>Check-in Successful!</b>\n\n"
        f"🎁 Base reward: +{POINTS_DAILY} SP\n"
        f"🔥 Streak bonus: +{bonus} SP\n"
        f"📈 Current streak: {streak} day(s)\n\n"
        f"<b>Total earned:</b> +{total} SP",
        parse_mode=ParseMode.HTML,
        reply_markup=back_menu(),
    )
