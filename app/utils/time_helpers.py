from datetime import datetime, timezone


def relative_time_ar(dt: datetime) -> str:
    """Return a human-friendly relative time string in Arabic."""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = now - dt
    minutes = int(diff.total_seconds() / 60)

    if minutes < 1:
        return "الآن"
    elif minutes < 60:
        if minutes == 1:
            return "منذ دقيقة"
        elif minutes == 2:
            return "منذ دقيقتين"
        elif minutes <= 10:
            return f"منذ {minutes} دقائق"
        else:
            return f"منذ {minutes} دقيقة"
    elif minutes < 1440:
        hours = minutes // 60
        if hours == 1:
            return "منذ ساعة"
        elif hours == 2:
            return "منذ ساعتين"
        elif hours <= 10:
            return f"منذ {hours} ساعات"
        else:
            return f"منذ {hours} ساعة"
    else:
        days = minutes // 1440
        if days == 1:
            return "منذ يوم"
        elif days == 2:
            return "منذ يومين"
        elif days <= 10:
            return f"منذ {days} أيام"
        else:
            return f"منذ {days} يوم"
