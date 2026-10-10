from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from config import BOT_USERNAME, POINTS_INVITE
import database as db


async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = await db.get_user(user_id)

    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    share_text = (
        f"🎁 Join VIP Stake and earn free rewards!\n"
        f"Use my link: {link}"
    )
    share_url = f"https://t.me/share/url?url={link}&text={share_text}"

    text = (
        "🔗 <b>Invite Friends</b>\n\n"
        f"Earn <b>+{POINTS_INVITE} SP</b> for every friend who joins using your link!\n\n"
        f"<b>Your invites:</b> {user['invite_count']}\n\n"
        f"<b>Your link:</b>\n<code>{link}</code>"
    )
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 Share Link", url=share_url)],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu")],
    ])
    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=kb)


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    rows = await db.get_leaderboard(10)

    medals = ["🥇", "🥈", "🥉"]
    lines = ["🏆 <b>Top 10 Leaderboard</b>\n"]
    for i, r in enumerate(rows):
        prefix = medals[i] if i < 3 else f"{i+1}."
        name = r["first_name"] or r["username"] or "Anonymous"
        lines.append(f"{prefix} {name} — <b>{r['points']} SP</b>")

    from keyboards import back_menu
    await query.edit_message_text(
        "\n".join(lines), parse_mode=ParseMode.HTML, reply_markup=back_menu()
    )
