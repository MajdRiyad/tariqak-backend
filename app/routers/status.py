from datetime import datetime, timedelta, timezone
from fastapi import APIRouter
from app.llm.analyzer import analyze_all_checkpoints
from app.models import StatusResponse

router = APIRouter()

# Simple in-memory cache to avoid hammering the LLM
_cache: StatusResponse | None = None
_cache_time: datetime | None = None
CACHE_TTL = timedelta(minutes=10)


@router.get("/", response_model=StatusResponse)
async def get_status():
    """Get current status of all major checkpoints."""
    global _cache, _cache_time
    now = datetime.now(timezone.utc)

    if _cache and _cache_time and (now - _cache_time) < CACHE_TTL:
        return _cache

    checkpoints = await analyze_all_checkpoints()
    _cache = StatusResponse(checkpoints=checkpoints, generated_at=now)
    _cache_time = now
    return _cache
