"""
VIP Stake Bot - Single File Edition
Loyalty & rewards bot. No gambling. Telegram Ads friendly.
"""

import sqlite3
import logging
from datetime import datetime, date, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ============================================================
# CONFIG — REPLACE THESE
# ============================================================
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"
ADMIN_IDS = [123456789]  # Replace with your Telegram user ID

POINTS_DAILY = 10
POINTS_INVITE = 50
POINTS_TASK = 25

DB_PATH = "vip_stake.db"

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ============================================================
# DATABASE
# ============================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            points INTEGER DEFAULT 0,
            last_checkin TEXT,
            invited_by INTEGER,
            invites INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, username, points, last_checkin, invited_by, invites FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row


def create_user(user_id, username, invited_by=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO users (user_id, username, points, invited_by) VALUES (?, ?, 0, ?)",
        (user_id, username, invited_by),
    )
    conn.commit()
    conn.close()


def add_points(user_id, amount):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()


def set_checkin(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET last_checkin = ? WHERE user_id = ?", (date.today().isoformat(), user_id))
    conn.commit()
    conn.close()


def add_invite(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET invites = invites + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


# ============================================================
# HELPERS
# ============================================================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🎁 Daily Check-in", callback_data="checkin")],
        [InlineKeyboardButton("🔗 Invite Friends", callback_data="invite")],
        [InlineKeyboardButton("🏆 My Points", callback_data="points")],
        [InlineKeyboardButton("💎 VIP Tiers", callback_data="tiers")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
    ]
    return InlineKeyboardMarkup(keyboard)


def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="menu")]])


def get_tier(points):
    if points >= 5000:
        return "👑 Diamond VIP"
    if points >= 2000:
        return "💎 Platinum VIP"
    if points >= 1000:
        return "🥇 Gold VIP"
    if points >= 500:
        return "🥈 Silver VIP"
    if points >= 100:
        return "🥉 Bronze VIP"
    return "🌱 Starter"


# ============================================================
# COMMANDS
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    invited_by = None
    if args and args[0].startswith("ref_"):
        try:
            inviter_id = int(args[0].replace("ref_", ""))
            if inviter_id != user.id:
                invited_by = inviter_id
        except ValueError:
            pass

    existing = get_user(user.id)
    if not existing:
        create_user(user.id, user.username or user.first_name, invited_by)
        if invited_by:
            add_points(invited_by, POINTS_INVITE)
            add_invite(invited_by)

    text = (
        f"👋 Welcome to *VIP Stake*, {user.first_name}!\n\n"
        "🎁 Earn Stake Points by checking in daily, inviting friends, and completing tasks.\n"
        "🏆 Climb VIP tiers and unlock exclusive perks.\n\n"
        "✅ 100% free\n"
        "✅ No gambling, no betting, no real-money wagering\n"
        "✅ Transparent point system\n\n"
        "Choose an option below to begin 👇"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu())


async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 Main Menu", reply_markup=main_menu())


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *Commands*\n\n"
        "/start - Welcome & main menu\n"
        "/menu - Show main menu\n"
        "/checkin - Claim daily points\n"
        "/invite - Get your referral link\n"
        "/points - View your balance\n"
        "/tiers - See VIP tiers\n"
        "/help - This message\n\n"
        "No gambling. Rewards only. 🎁"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def checkin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    row = get_user(user.id)
    if not row:
        create_user(user.id, user.username or user.first_name)
        row = get_user(user.id)

    last_checkin = row[3]
    today = date.today().isoformat()

    if last_checkin == today:
        await update.message.reply_text("⏳ You already checked in today. Come back tomorrow!")
        return

    add_points(user.id, POINTS_DAILY)
    set_checkin(user.id)
    new_balance = get_user(user.id)[2]
    await update.message.reply_text(
        f"✅ Check-in complete! +{POINTS_DAILY} Stake Points\n"
        f"💰 Balance: {new_balance} points\n"
        f"🏅 Tier: {get_tier(new_balance)}"
    )


async def invite_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_username = context.bot.username
    user_id = update.effective_user.id
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    row = get_user(user_id)
    invites = row[5] if row else 0
    await update.message.reply_text(
        f"🔗 *Your Invite Link*\n\n`{link}`\n\n"
        f"👥 Friends invited: {invites}\n"
        f"🎁 Earn {POINTS_INVITE} points per friend who joins!",
        parse_mode="Markdown",
    )


async def points_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    row = get_user(user.id)
    if not row:
        create_user(user.id, user.username or user.first_name)
        row = get_user(user.id)

    points = row[2]
    invites = row[5]
    tier = get_tier(points)
    await update.message.reply_text(
        f"💰 *Your Stake Points*\n\n"
        f"Points: {points}\n"
        f"Tier: {tier}\n"
        f"Invites: {invites}",
        parse_mode="Markdown",
    )


async def tiers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💎 *VIP Tiers*\n\n"
        "🌱 Starter — 0+\n"
        "🥉 Bronze VIP — 100+\n"
        "🥈 Silver VIP — 500+\n"
        "🥇 Gold VIP — 1,000+\n"
        "💎 Platinum VIP — 2,000+\n"
        "👑 Diamond VIP — 5,000+\n\n"
        "Keep earning points to climb! 🚀"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Admins only.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total = c.fetchone()[0]
    c.execute("SELECT SUM(points) FROM users")
    total_points = c.fetchone()[0] or 0
    conn.close()

    await update.message.reply_text(
        f"🛠️ *Admin Panel*\n\n"
        f"👥 Users: {total}\n"
        f"💰 Total points in circulation: {total_points}",
        parse_mode="Markdown",
    )


# ============================================================
# CALLBACKS
# ============================================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user

    if data == "menu":
        await query.edit_message_text("📋 Main Menu", reply_markup=main_menu())
        return

    if data == "checkin":
        row = get_user(user.id)
        if not row:
            create_user(user.id, user.username or user.first_name)
            row = get_user(user.id)
        last = row[3]
        today = date.today().isoformat()
        if last == today:
            await query.edit_message_text(
                "⏳ You already checked in today. Come back tomorrow!",
                reply_markup=back_menu(),
            )
            return
        add_points(user.id, POINTS_DAILY)
        set_checkin(user.id)
        bal = get_user(user.id)[2]
        await query.edit_message_text(
            f"✅ Check-in complete! +{POINTS_DAILY} points\n"
            f"💰 Balance: {bal}\n"
            f"🏅 Tier: {get_tier(bal)}",
            reply_markup=back_menu(),
        )
        return

    if data == "invite":
        link = f"https://t.me/{context.bot.username}?start=ref_{user.id}"
        row = get_user(user.id)
        invites = row[5] if row else 0
        await query.edit_message_text(
            f"🔗 Your invite link:\n{link}\n\n"
            f"👥 Invites: {invites}\n"
            f"🎁 +{POINTS_INVITE} points per friend!",
            reply_markup=back_menu(),
        )
        return

    if data == "points":
        row = get_user(user.id)
        if not row:
            create_user(user.id, user.username or user.first_name)
            row = get_user(user.id)
        await query.edit_message_text(
            f"💰 Points: {row[2]}\n🏅 Tier: {get_tier(row[2])}\n👥 Invites: {row[5]}",
            reply_markup=back_menu(),
        )
        return

    if data == "tiers":
        text = (
            "💎 VIP Tiers\n\n"
            "🌱 Starter — 0+\n"
            "🥉 Bronze — 100+\n"
            "🥈 Silver — 500+\n"
            "🥇 Gold — 1,000+\n"
            "💎 Platinum — 2,000+\n"
            "👑 Diamond — 5,000+"
        )
        await query.edit_message_text(text, reply_markup=back_menu())
        return

    if data == "about":
        text = (
            "ℹ️ VIP Stake\n\n"
            "A loyalty & rewards bot. Earn Stake Points via tasks, check-ins and invites. "
            "Redeem for perks and VIP status tiers.\n\n"
            "✅ Free to use\n"
            "✅ No gambling or real-money wagering\n"
            "✅ Community-driven rewards"
        )
        await query.edit_message_text(text, reply_markup=back_menu())
        return


# ============================================================
# ERROR HANDLER
# ============================================================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling update:", exc_info=context.error)


# ============================================================
# MAIN
# ============================================================
def main():
    init_db()

    if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Set your BOT_TOKEN in the file before running.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("checkin", checkin_cmd))
    app.add_handler(CommandHandler("invite", invite_cmd))
    app.add_handler(CommandHandler("points", points_cmd))
    app.add_handler(CommandHandler("tiers", tiers_cmd))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.add_error_handler(error_handler)

    print("🚀 VIP Stake Bot is running... Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
