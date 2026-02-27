from fastapi import APIRouter, Query
from app.database import get_db
from app.models import MessageOut

router = APIRouter()


@router.get("/", response_model=list[MessageOut])
async def get_messages(limit: int = Query(default=50, le=200)):
    """Get recent raw messages from the database."""
    db = await get_db()
    cursor = await db.execute(
        "SELECT id, channel_name, text, timestamp FROM messages "
        "ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    )
    rows = await cursor.fetchall()
    return [MessageOut(**dict(row)) for row in rows]
