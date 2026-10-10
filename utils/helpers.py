import time
from config import TIERS


def get_tier(points: int):
    current = TIERS[0]
    for tier in TIERS:
        if points >= tier[1]:
            current = tier
    return current


def next_tier(points: int):
    for tier in TIERS:
        if points < tier[1]:
            return tier
    return None


def format_profile(user: dict):
    points = user["points"]
    name, threshold, emoji = get_tier(points)
    nxt = next_tier(points)

    text = (
        f"👤 <b>Your Profile</b>\n\n"
        f"<b>Name:</b> {user['first_name']}\n"
        f"<b>Stake Points:</b> {points} SP\n"
        f"<b>Total Earned:</b> {user['total_earned']} SP\n"
        f"<b>Invites:</b> {user['invite_count']}\n"
        f"<b>Daily Streak:</b> {user['streak']} day(s)\n\n"
        f"<b>Tier:</b> {emoji} {name}\n"
    )
    if nxt:
        remaining = nxt[1] - points
        text += f"<b>Next Tier:</b> {nxt[2]} {nxt[0]} — {remaining} SP to go"
    else:
        text += "👑 You've reached the highest tier!"
    return text


def can_checkin(last_daily: int):
    return int(time.time()) - last_daily >= 86400
