from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from handlers import start, tasks, invites, rewards, admin

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start.start))
    app.add_handler(CommandHandler("checkin", tasks.checkin))
    app.add_handler(CommandHandler("invite", invites.invite))
    app.add_handler(CommandHandler("rewards", rewards.rewards))
    app.add_handler(CommandHandler("admin", admin.panel))

    app.run_polling()

if __name__ == "__main__":
    main()
