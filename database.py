import aiosqlite
import time

DB_PATH = "vipstake.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                points INTEGER DEFAULT 0,
                total_earned INTEGER DEFAULT 0,
                invited_by INTEGER,
                invite_count INTEGER DEFAULT 0,
                last_daily INTEGER DEFAULT 0,
                streak INTEGER DEFAULT 0,
                joined_at INTEGER
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS task_completions (
                user_id INTEGER,
                task_id TEXT,
                completed_at INTEGER,
                PRIMARY KEY (user_id, task_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS redemptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reward_name TEXT,
                cost INTEGER,
                redeemed_at INTEGER
            )
        """)
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def create_user(user_id: int, username: str, first_name: str, invited_by: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name, invited_by, joined_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, first_name, invited_by, int(time.time())))
        await db.commit()


async def update_points(user_id: int, delta: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET points = points + ?, total_earned = total_earned + ?
            WHERE user_id = ?
        """, (delta, max(delta, 0), user_id))
        await db.commit()


async def add_invite(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET invite_count = invite_count + 1 WHERE user_id = ?
        """, (user_id,))
        await db.commit()


async def set_last_daily(user_id: int, ts: int, streak: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            UPDATE users SET last_daily = ?, streak = ? WHERE user_id = ?
        """, (ts, streak, user_id))
        await db.commit()


async def is_task_done(user_id: int, task_id: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM task_completions WHERE user_id=? AND task_id=?",
            (user_id, task_id),
        ) as cur:
            return await cur.fetchone() is not None


async def complete_task(user_id: int, task_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO task_completions (user_id, task_id, completed_at)
            VALUES (?, ?, ?)
        """, (user_id, task_id, int(time.time())))
        await db.commit()


async def log_redemption(user_id: int, reward_name: str, cost: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO redemptions (user_id, reward_name, cost, redeemed_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, reward_name, cost, int(time.time())))
        await db.commit()


async def get_leaderboard(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT first_name, username, points FROM users
            ORDER BY points DESC LIMIT ?
        """, (limit,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


async def stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cur:
            users = (await cur.fetchone())[0]
        async with db.execute("SELECT SUM(points) FROM users") as cur:
            points = (await cur.fetchone())[0] or 0
        async with db.execute("SELECT COUNT(*) FROM redemptions") as cur:
            redemptions = (await cur.fetchone())[0]
    return {"users": users, "points": points, "redemptions": redemptions}
