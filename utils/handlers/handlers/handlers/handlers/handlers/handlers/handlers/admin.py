from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import ADMIN_IDS
import database as db


def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if uid not in ADMIN_IDS:
            if update.message:
                await update.message.reply_text("⛔ Unauthorized.")
            return
        return await func(update, context)
    return wrapper


@admin_only
async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = await db.stats()
    await update.message.reply_text(
        f"📊 <b>Bot Stats</b>\n\n"
        f"👥 Users: {s['users']}\n"
        f"💰 Points in circulation: {s['points']}\n"
        f"🎁 Redemptions: {s['redemptions']}",
        parse_mode=ParseMode.HTML,
    )


@admin_only
async def give_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /give <user_id> <points>
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /give <user_id> <points>")
        return
    try:
        target = int(context.args[0])
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Invalid numbers.")
        return
    user = await db.get_user(target)
    if not user:
        await update.message.reply_text("User not found.")
        return
    await db.update_points(target, amount)
    await update.message.reply_text(f"✅ Gave {amount} SP to {target}.")
    try:
        await context.bot.send_message(target, f"🎁 Admin granted you {amount} SP!")
    except Exception:
        pass


@admin_only
async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    msg = " ".join(context.args)
    import aiosqlite
    from database import DB_PATH
    sent = 0
    async with aiosqlite.connect(DB_PATH) as db_conn:
        async with db_conn.execute("SELECT user_id FROM users") as cur:
            rows = await cur.fetchall()
    for (uid,) in rows:
        try:
            await context.bot.send_message(uid, msg)
            sent += 1
        except Exception:
            pass
    await update.message.reply_text(f"✅ Broadcast sent to {sent} users.")
