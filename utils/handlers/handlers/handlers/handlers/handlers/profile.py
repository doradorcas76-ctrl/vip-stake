from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import database as db
from utils.helpers import format_profile
from keyboards import back_menu


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = await db.get_user(query.from_user.id)
    if not user:
        await query.edit_message_text("Please send /start first.")
        return
    await query.edit_message_text(
        format_profile(user), parse_mode=ParseMode.HTML, reply_markup=back_menu()
    )
