from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Profile", callback_data="profile"),
         InlineKeyboardButton("✅ Daily Check-in", callback_data="daily")],
        [InlineKeyboardButton("📋 Tasks", callback_data="tasks"),
         InlineKeyboardButton("🎁 Rewards Shop", callback_data="rewards")],
        [InlineKeyboardButton("🔗 Invite Friends", callback_data="invite"),
         InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about"),
         InlineKeyboardButton("❓ Help", callback_data="help")],
    ])


def back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu")]
    ])


def tasks_menu(done_ids):
    rows = []
    from config import TASKS
    for tid, title, _, pts, _ in TASKS:
        mark = "✅" if tid in done_ids else "🔓"
        rows.append([InlineKeyboardButton(f"{mark} {title} • +{pts}", callback_data=f"task:{tid}")])
    rows.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def rewards_menu():
    rows = []
    from config import REWARDS
    for i, (name, cost, _) in enumerate(REWARDS):
        rows.append([InlineKeyboardButton(f"{name} — {cost} SP", callback_data=f"redeem:{i}")])
    rows.append([InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu")])
    return InlineKeyboardMarkup(rows)


def task_verify_menu(task_id: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ I Completed This", callback_data=f"verify:{task_id}")],
        [InlineKeyboardButton("⬅️ Back", callback_data="tasks")],
    ])
