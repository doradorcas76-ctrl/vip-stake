from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import database as db
from keyboards import main_menu

WELCOME = (
    "🎁 <b>Welcome to VIP Stake!</b>\n\n"
    "Your all-in-one loyalty & rewards companion on Telegram.\n\n"
    "Earn <b>Stake Points (SP)</b> by completing simple tasks, daily "
    "check-ins, inviting friends, and staying active in our community. "
    "Redeem points for exclusive perks, digital rewards, and VIP status tiers.\n\n"
    "✅ 100% free to use\n"
    "✅ No gambling, no betting, no real-money wagering\n"
    "✅ Transparent point system\n"
    "✅ Community-driven rewards\n\n"
    "Start staking your points today and unlock your VIP journey! 🚀"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    invited_by = None

    if context.args:
        try:
            invited_by = int(context.args[0])
            if invited_by == user.id:
                invited_by = None
        except ValueError:
            invited_by = None

    existing = await db.get_user(user.id)
    if not existing:
        await db.create_user(user.id, user.username or "", user.first_name, invited_by)
        if invited_by:
            inviter = await db.get_user(invited_by)
            if inviter:
                from config import POINTS_INVITE
                await db.update_points(invited_by, POINTS_INVITE)
                await db.add_invite(invited_by)
                try:
                    await context.bot.send_message(
                        invited_by,
                        f"🎉 Someone joined using your invite link! +{POINTS_INVITE} SP"
                    )
                except Exception:
                    pass

    await update.message.reply_text(
        WELCOME, parse_mode=ParseMode.HTML, reply_markup=main_menu()
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        WELCOME, parse_mode=ParseMode.HTML, reply_markup=main_menu()
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "ℹ️ <b>About VIP Stake</b>\n\n"
        "Loyalty & rewards bot. Earn Stake Points via tasks, check-ins & invites. "
        "Redeem for perks.\n\n"
        "<b>Important:</b> VIP Stake is 100% free, and is <b>not</b> a gambling bot. "
        "There is no betting, no wagering, and no real-money involvement of any kind. "
        "All rewards are digital community perks only."
    )
    from keyboards import back_menu
    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=back_menu())


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "❓ <b>How it works</b>\n\n"
        "1️⃣ <b>Daily Check-in</b> — claim free SP every 24h. Longer streaks = more SP.\n"
        "2️⃣ <b>Tasks</b> — complete simple actions to earn SP.\n"
        "3️⃣ <b>Invite Friends</b> — get bonus SP for each friend who joins.\n"
        "4️⃣ <b>Rewards Shop</b> — redeem SP for digital perks & VIP tiers.\n\n"
        "Need help? Contact support."
    )
    from keyboards import back_menu
    await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=back_menu())
