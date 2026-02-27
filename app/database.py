import aiosqlite
from app.config import settings

DB_PATH = settings.database_path
_db: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    global _db
    if _db is None:
        _db = await aiosqlite.connect(DB_PATH)
        _db.row_factory = aiosqlite.Row
    return _db


async def init_db():
    db = await get_db()
    await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_name TEXT NOT NULL,
            message_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(channel_name, message_id)
        )
    """)
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_messages_timestamp
        ON messages(timestamp DESC)
    """)
    await db.commit()


async def close_db():
    global _db
    if _db:
        await _db.close()
        _db = None
