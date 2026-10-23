"""Date formatter — relative and absolute date formatting."""

from datetime import datetime, timezone, timedelta


def format_relative(*, timestamp: str) -> dict:
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return {"error": "Invalid timestamp"}
    now = datetime.now(timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 0:
        return {"relative": "in the future", "absolute": dt.strftime("%Y-%m-%d %H:%M"), "ago": False}
    if seconds < 60:
        rel = "just now"
    elif seconds < 3600:
        m = seconds // 60
        rel = f"{m}m ago"
    elif seconds < 86400:
        h = seconds // 3600
        rel = f"{h}h ago"
    elif seconds < 604800:
        d = seconds // 86400
        rel = f"{d}d ago"
    elif seconds < 2592000:
        w = seconds // 604800
        rel = f"{w}w ago"
    else:
        rel = dt.strftime("%b %d, %Y")
    return {"relative": rel, "absolute": dt.strftime("%Y-%m-%d %H:%M UTC"), "ago": True}


def format_duration(*, seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}h {m}m"
