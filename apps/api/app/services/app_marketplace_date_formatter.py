"""Date formatter — human-friendly date formatting for marketplace UI."""

from datetime import datetime, timezone


def format_relative_time(*, iso_date: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - dt
        seconds = int(diff.total_seconds())
        if seconds < 0:
            return "just now"
        if seconds < 60:
            return "just now"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes}m ago"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h ago"
        days = hours // 24
        if days < 7:
            return f"{days}d ago"
        if days < 30:
            weeks = days // 7
            return f"{weeks}w ago"
        if days < 365:
            months = days // 30
            return f"{months}mo ago"
        years = days // 365
        return f"{years}y ago"
    except (ValueError, TypeError):
        return iso_date


def format_date_short(*, iso_date: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except (ValueError, TypeError):
        return iso_date


def format_date_range(*, start: str, end: str) -> str:
    s = format_date_short(iso_date=start)
    e = format_date_short(iso_date=end)
    return f"{s} — {e}"
