from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import database as db
from config import REWARDS, ADMIN_IDS, SUPPORT_USERNAME
from keyboards import rewards_menu, back_menu


async def rewards_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = await db.get_user(query.from_user.id)

    text = (
        "🎁 <b>Rewards Shop</b>\n\n"
        f"Your balance: <b>{user['points']} SP</b>\n\n"
        "Redeem your Stake Points for exclusive digital perks and VIP status tiers.\n\n"
        "<i>All rewards are digital community perks only — no cash value.</i>"
    )
    await query.edit_message_text(
        text, parse_mode=ParseMode.HTML, reply_markup=rewards_menu()
    )


async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    idx = int(query.data.split(":", 1)[1])
    name, cost, desc = REWARDS[idx]
    user = await db.get_user(query.from_user.id)

    if user["points"] < cost:
        await query.answer(
            f"❌ You need {cost - user['points']} more SP.", show_alert=True
        )
        return

    await db.update_points(user["user_id"], -cost)
    await db.log_redemption(user["user_id"], name, cost)

    await query.edit_message_text(
        f"🎉 <b>Redemption Successful!</b>\n\n"
        f"<b>Reward:</b> {name}\n"
        f"<b>Cost:</b> {cost} SP\n\n"
        f"{desc}\n\n"
        f"Our team will process your reward shortly. "
        f"Contact {SUPPORT_USERNAME} if you have any questions.",
        parse_mode=ParseMode.HTML,
        reply_markup=back_menu(),
    )

    # notify admins
    for admin in ADMIN_IDS:
        try:
            await context.bot.send_message(
                admin,
                f"🔔 Redemption: user <code>{user['user_id']}</code> "
                f"redeemed <b>{name}</b> for {cost} SP.",
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
