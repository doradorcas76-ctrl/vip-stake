# VIP Stake Telegram Bot

🎁 Loyalty & rewards bot. Earn Stake Points via tasks, check-ins & invites.
Redeem for perks. Free, no gambling.

## ✅ Compliance Notes (Telegram Ads Friendly)

- ❌ No gambling, betting, or wagering of any kind.
- ❌ No real-money transactions, crypto, or cash prizes.
- ✅ Rewards are **digital community perks only** (badges, status, shoutouts).
- ✅ Clearly labeled as "100% free to use".
- ✅ No external payment links.

## 🚀 Setup

1. **Clone / copy files** into a folder.
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Create a bot** on Telegram via [@BotFather](https://t.me/BotFather), copy the token.
4. **Copy `.env.example` to `.env`** and fill in:
   ```
   BOT_TOKEN=...
   ADMIN_IDS=your_telegram_id
   BOT_USERNAME=YourBotUsername
   SUPPORT_USERNAME=@YourSupport
   ```
5. **Run:**
   ```bash
   python bot.py
   ```

## 📋 Features

- 👤 User profiles with tier system (Bronze → VIP Elite)
- ✅ Daily check-in with streak bonuses
- 📋 Tasks for one-time SP rewards
- 🔗 Referral/invite system
- 🎁 Rewards shop with admin notifications
- 🏆 Leaderboard
- 🛠 Admin commands: `/stats`, `/give`, `/broadcast`

## 🎯 Points Economy (editable in `config.py`)

| Action | Points |
|---|---|
| Daily check-in | 10 (+streak bonus) |
| Invite friend | 50 |
| Task completion | 10–40 |

## 📜 License

MIT — use freely, modify for your community.
