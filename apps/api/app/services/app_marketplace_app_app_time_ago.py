"""Time ago — human-readable relative time formatting."""

from datetime import datetime, timedelta


def time_ago(*, timestamp: str, now: str | None = None) -> dict:
    try:
        dt = datetime.fromisoformat(timestamp)
    except ValueError:
        return {"error": "Invalid timestamp"}
    current = datetime.fromisoformat(now) if now else datetime.utcnow()
    delta = current - dt
    seconds = int(delta.total_seconds())
    if seconds < 0:
        return {"text": "in the future", "seconds": seconds}
    if seconds < 60:
        return {"text": "just now", "seconds": seconds}
    minutes = seconds // 60
    if minutes < 60:
        return {"text": f"{minutes}m ago", "seconds": seconds}
    hours = minutes // 60
    if hours < 24:
        return {"text": f"{hours}h ago", "seconds": seconds}
    days = hours // 24
    if days < 30:
        return {"text": f"{days}d ago", "seconds": seconds}
    months = days // 30
    if months < 12:
        return {"text": f"{months}mo ago", "seconds": seconds}
    years = months // 12
    return {"text": f"{years}y ago", "seconds": seconds}
