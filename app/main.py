import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, close_db, get_db
from app.scraper.scheduler import start_scheduler, stop_scheduler
from app.routers import status, query, messages

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def _seed_if_empty():
    """Auto-seed sample data if the database is empty."""
    from datetime import datetime, timedelta, timezone

    db = await get_db()
    cursor = await db.execute("SELECT COUNT(*) FROM messages")
    row = await cursor.fetchone()
    if row[0] > 0:
        return

    logger.info("Database empty, seeding sample data...")
    now = datetime.now(timezone.utc)
    samples = [
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
    for channel, msg_id, text, minutes_ago in samples:
        ts = (now + timedelta(minutes=minutes_ago)).isoformat()
        await db.execute(
            "INSERT OR IGNORE INTO messages (channel_name, message_id, text, timestamp) VALUES (?, ?, ?, ?)",
            (channel, msg_id, text, ts),
        )
    await db.commit()
    logger.info("Seeded 14 sample messages.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Tariqak API...")
    await init_db()
    await _seed_if_empty()
    await start_scheduler()
    yield
    logger.info("Shutting down Tariqak API...")
    await stop_scheduler()
    await close_db()


app = FastAPI(
    title="Tariqak API - طريقك",
    description="West Bank Road Assistant API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status.router, prefix="/status", tags=["status"])
app.include_router(query.router, prefix="/query", tags=["query"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])


@app.get("/health")
async def health():
    return {"status": "ok", "app": "tariqak"}
