import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
DB_PATH = "vip_stake.db"

POINTS = {
    "daily_checkin": 10,
    "invite": 50,
    "task_complete": 25,
}
