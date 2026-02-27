"""
Seed the SQLite database with sample road condition messages for testing.
Run: python seed_test_data.py
"""
import sqlite3
from datetime import datetime, timedelta, timezone

DB_PATH = "./tariqak.db"

SAMPLE_MESSAGES = [
    ("ahwalaltreq", 1001, "حاجز قلنديا سالك هلأ والتفتيش خفيف", -30),
    ("ahwalaltreq", 1002, "الكونتينر سالك والحمد لله، ما في تفتيش", -120),
    ("ahwalaltreq", 1003, "حاجز عناب سالك بدون تفتيش والطريق فاضية", -15),
    ("ahwalaltreq", 1004, "قلنديا صار في أزمة، الطابور طويل كتير والتفتيش بطيء", -10),
    ("ahwalaltreq", 1005, "وادي النار سالك ومفتوح بالاتجاهين", -45),
    ("a7walstreet", 2001, "حاجز حوارة مسكر بالكامل، الجيش عامل حاجز طيّار", -45),
    ("a7walstreet", 2002, "حاجز جبع أزمة خفيفة بس ماشي الحال، صف سيارات قصير", -60),
    ("a7walstreet", 2003, "حاجز زعترة في أزمة خنقة، صف طويل من السيارات بالاتجاهين", -90),
    ("a7walstreet", 2004, "طريق المعرجات سالك لكن في تواجد عسكري خفيف", -20),
    ("Palestine_Streets_Radar", 3001, "أزمة خنقة على حاجز زعترة، حاسبوا حالكم", -85),
    ("Palestine_Streets_Radar", 3002, "حوارة لسا مسكر، استخدموا طريق بديل", -40),
    ("Palestine_Streets_Radar", 3003, "قلنديا أزمة خنقة من ساعة تقريباً", -25),
    ("Palestine_Streets_Radar", 3004, "عين سينيا سالكة والحمد لله", -50),
    ("Palestine_Streets_Radar", 3005, "عيون حرامية منطقة هادية وسالكة", -70),
]


def seed():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_name TEXT NOT NULL,
        message_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(channel_name, message_id)
    )"""
    )
    conn.execute(
        """CREATE INDEX IF NOT EXISTS idx_messages_timestamp
        ON messages(timestamp DESC)"""
    )

    now = datetime.now(timezone.utc)
    count = 0
    for channel, msg_id, text, minutes_ago in SAMPLE_MESSAGES:
        ts = (now + timedelta(minutes=minutes_ago)).isoformat()
        try:
            conn.execute(
                "INSERT OR IGNORE INTO messages "
                "(channel_name, message_id, text, timestamp) VALUES (?, ?, ?, ?)",
                (channel, msg_id, text, ts),
            )
            count += 1
        except Exception as e:
            print(f"Error inserting message {msg_id}: {e}")

    conn.commit()
    conn.close()
    print(f"Seeded {count} messages into {DB_PATH}")


if __name__ == "__main__":
    seed()
