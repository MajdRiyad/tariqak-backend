import json
import logging
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.llm.ollama_client import generate
from app.llm.prompts import STATUS_SYSTEM_PROMPT, CHAT_SYSTEM_PROMPT
from app.utils.locations import CHECKPOINTS, find_locations_in_text
from app.utils.time_helpers import relative_time_ar
from app.models import CheckpointStatus

logger = logging.getLogger(__name__)

# Main dashboard checkpoints (first 6)
DASHBOARD_CHECKPOINTS = CHECKPOINTS[:6]

STATUS_COLOR_MAP = {
    "سالكة": "green",
    "مسكرة": "red",
    "أزمة خنقة": "orange",
    "غير معروف": "grey",
}

# Keywords that indicate road status in messages
CLEAR_KEYWORDS = ["سالك", "سالكة", "فاضي", "فاضية", "مفتوح", "بدون تفتيش"]
CLOSED_KEYWORDS = ["مسكر", "مسكرة", "مغلق", "مغلقة", "حاجز طيّار", "حاجز طيار"]
CROWDED_KEYWORDS = ["أزمة", "خنقة", "ازدحام", "طابور", "بطيء", "زحمة"]


def _detect_status_from_text(text: str) -> str:
    """Detect road status from message text using keyword matching."""
    for kw in CLOSED_KEYWORDS:
        if kw in text:
            return "مسكرة"
    for kw in CROWDED_KEYWORDS:
        if kw in text:
            return "أزمة خنقة"
    for kw in CLEAR_KEYWORDS:
        if kw in text:
            return "سالكة"
    return "غير معروف"


async def _get_recent_messages(hours: int = 6) -> list[dict]:
    """Fetch messages from the last N hours."""
    db = await get_db()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    cursor = await db.execute(
        "SELECT text, timestamp, channel_name FROM messages "
        "WHERE timestamp > ? ORDER BY timestamp DESC",
        (cutoff,),
    )
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


def _analyze_locally(messages: list[dict]) -> list[CheckpointStatus]:
    """Keyword-based analysis fallback when Ollama is unavailable."""
    results = []

    for cp in DASHBOARD_CHECKPOINTS:
        status = "غير معروف"
        summary = "ما في تقارير حديثة"
        last_update = "لا يوجد تحديثات"

        # Find messages mentioning this checkpoint
        for m in messages:
            text = m["text"]
            if any(kw in text for kw in cp.keywords):
                status = _detect_status_from_text(text)
                # Use a snippet of the message as summary
                summary = text[:80] + ("..." if len(text) > 80 else "")
                try:
                    ts = datetime.fromisoformat(m["timestamp"])
                    last_update = relative_time_ar(ts)
                except (ValueError, TypeError):
                    last_update = "غير معروف"
                break

        color = STATUS_COLOR_MAP.get(status, "grey")
        results.append(
            CheckpointStatus(
                name_ar=cp.name_ar,
                name_en=cp.name_en,
                status=status,
                color=color,
                last_update=last_update,
                summary=summary,
            )
        )

    return results


def _build_chat_response(question: str, messages: list[dict]) -> str:
    """Keyword-based chat response fallback when Ollama is unavailable."""
    # Find which locations the user is asking about
    relevant_messages = []
    for loc in CHECKPOINTS:
        if any(kw in question for kw in loc.keywords) or loc.name_ar in question:
            for m in messages:
                if any(kw in m["text"] for kw in loc.keywords):
                    relevant_messages.append((loc, m))
            break

    if not relevant_messages:
        # General question - return summary of recent activity
        if not messages:
            return "ما في تحديثات حديثة هلأ. جرب تسأل بعدين."

        recent = messages[:5]
        lines = ["هاي آخر الأخبار اللي عنا:\n"]
        for m in recent:
            try:
                ts = datetime.fromisoformat(m["timestamp"])
                time_str = relative_time_ar(ts)
            except (ValueError, TypeError):
                time_str = ""
            lines.append(f"• {m['text'][:100]} ({time_str})")
        return "\n".join(lines)

    # Found relevant messages
    loc, msg = relevant_messages[0]
    status = _detect_status_from_text(msg["text"])
    try:
        ts = datetime.fromisoformat(msg["timestamp"])
        time_str = relative_time_ar(ts)
    except (ValueError, TypeError):
        time_str = ""

    return (
        f"حسب آخر التقارير ({time_str}):\n"
        f"{loc.name_ar}: {status}\n"
        f"التفاصيل: {msg['text'][:150]}"
    )


async def analyze_all_checkpoints() -> list[CheckpointStatus]:
    """Generate status summary for all major checkpoints."""
    messages = await _get_recent_messages(hours=6)

    if not messages:
        return [
            CheckpointStatus(
                name_ar=cp.name_ar,
                name_en=cp.name_en,
                status="غير معروف",
                color="grey",
                last_update="لا يوجد تحديثات",
                summary="ما في تقارير حديثة",
            )
            for cp in DASHBOARD_CHECKPOINTS
        ]

    # Try Ollama first, fall back to local keyword analysis
    try:
        messages_text = "\n".join(
            f"[{m['timestamp']}] ({m['channel_name']}): {m['text']}"
            for m in messages[:80]
        )

        checkpoint_names = ", ".join(cp.name_ar for cp in DASHBOARD_CHECKPOINTS)
        user_prompt = (
            f"حلّل الرسائل التالية من قنوات تلغرام وأعطني حالة كل حاجز من هاي الحواجز: "
            f"{checkpoint_names}\n\n"
            f"الرسائل:\n{messages_text}"
        )

        raw_response = await generate(STATUS_SYSTEM_PROMPT, user_prompt)

        # Check if Ollama returned an empty/fallback response
        if raw_response.strip() in ('{"checkpoints": []}', ""):
            logger.info("Ollama unavailable, using local keyword analysis.")
            return _analyze_locally(messages)

        return _parse_status_response(raw_response, messages)

    except Exception as e:
        logger.warning(f"LLM analysis failed ({e}), using local keyword analysis.")
        return _analyze_locally(messages)


def _parse_status_response(
    raw: str, messages: list[dict]
) -> list[CheckpointStatus]:
    """Parse the LLM JSON response into CheckpointStatus list."""
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        data = json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        logger.error(f"Failed to parse LLM response as JSON: {raw[:200]}")
        return _analyze_locally(messages)

    results = []
    llm_checkpoints = {
        cp["name_ar"]: cp for cp in data.get("checkpoints", [])
    }

    for cp in DASHBOARD_CHECKPOINTS:
        llm_cp = llm_checkpoints.get(cp.name_ar, {})
        status = llm_cp.get("status", "غير معروف")
        color = STATUS_COLOR_MAP.get(status, "grey")
        summary = llm_cp.get("summary", "ما في معلومات")

        # Find last message mentioning this checkpoint
        last_update = "غير معروف"
        for m in messages:
            if any(kw in m["text"] for kw in cp.keywords):
                try:
                    ts = datetime.fromisoformat(m["timestamp"])
                    last_update = relative_time_ar(ts)
                except (ValueError, TypeError):
                    last_update = "غير معروف"
                break

        results.append(
            CheckpointStatus(
                name_ar=cp.name_ar,
                name_en=cp.name_en,
                status=status,
                color=color,
                last_update=last_update,
                summary=summary,
            )
        )

    return results


async def answer_query(question: str) -> tuple[str, int]:
    """Answer a user question using recent messages as context."""
    messages = await _get_recent_messages(hours=12)

    # Try Ollama first
    try:
        messages_text = "\n".join(
            f"[{m['timestamp']}]: {m['text']}" for m in messages[:60]
        )

        user_prompt = (
            f"المعلومات المتوفرة من قنوات تلغرام:\n{messages_text}\n\n"
            f"سؤال المستخدم: {question}"
        )

        answer = await generate(CHAT_SYSTEM_PROMPT, user_prompt)

        if answer.strip() in ('{"checkpoints": []}', ""):
            logger.info("Ollama unavailable, using local chat response.")
            return _build_chat_response(question, messages), len(messages)

        return answer, len(messages)

    except Exception as e:
        logger.warning(f"LLM chat failed ({e}), using local response.")
        return _build_chat_response(question, messages), len(messages)
