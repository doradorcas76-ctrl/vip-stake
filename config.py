import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "VIPStakeBot")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "")

# Points configuration
POINTS_DAILY = 10
POINTS_INVITE = 50
POINTS_TASK_DEFAULT = 25
POINTS_SOCIAL = 20

# VIP Tiers (points threshold)
TIERS = [
    ("Bronze",   0,    "🥉"),
    ("Silver",   500,  "🥈"),
    ("Gold",     2000, "🥇"),
    ("Platinum", 5000, "💎"),
    ("VIP Elite", 15000, "👑"),
]

# Reward shop (name, cost, description)
REWARDS = [
    ("Custom Badge 🎖", 200,  "Show off a custom badge in your profile."),
    ("VIP Shoutout 📣", 500,  "Get a shoutout in our community channel."),
    ("Priority Support ⚡", 800, "Get faster responses from our team."),
    ("Exclusive Sticker Pack 🎨", 1200, "Unlock a VIP-only sticker pack."),
    ("Premium Emoji Set ✨", 2500, "Unlock premium emoji access perks."),
    ("VIP Elite Status 👑", 5000, "Instantly unlock VIP Elite tier perks."),
]

# Daily tasks (id, title, description, points, verify_type)
TASKS = [
    ("join_channel", "Join Our Channel", "Stay updated with the community.", 30, "channel"),
    ("follow_twitter", "Follow on Social", "Follow our social profile.", 20, "manual"),
    ("share_bot", "Share the Bot", "Share VIP Stake with 3 friends.", 40, "manual"),
    ("read_rules", "Read Community Rules", "Read and accept the rules.", 10, "auto"),
]
