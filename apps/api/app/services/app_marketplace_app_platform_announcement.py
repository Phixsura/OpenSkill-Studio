"""Platform announcement — publish platform-wide announcements."""

import secrets
import html
from datetime import datetime, timedelta


def create_announcement(*, title: str, content: str, audience: str = "all",
                          priority: str = "normal", expires_hours: int = 168) -> dict:
    valid_audiences = {"all", "developers", "users", "admins"}
    valid_priorities = {"low", "normal", "high", "urgent"}
    if audience not in valid_audiences:
        return {"error": f"Invalid audience. Valid: {', '.join(sorted(valid_audiences))}"}
    if priority not in valid_priorities:
        return {"error": f"Invalid priority. Valid: {', '.join(sorted(valid_priorities))}"}
    now = datetime.utcnow()
    return {
        "announcement_id": f"pann_{secrets.token_urlsafe(8)}",
        "title": html.escape(title),
        "content": html.escape(content),
        "audience": audience,
        "priority": priority,
        "published_at": now.isoformat(),
        "expires_at": (now + timedelta(hours=expires_hours)).isoformat(),
        "read_count": 0,
    }


def filter_announcements(*, announcements: list[dict], audience: str) -> dict:
    filtered = [a for a in announcements if a.get("audience") in (audience, "all")]
    filtered.sort(key=lambda a: {"urgent": 0, "high": 1, "normal": 2, "low": 3}.get(a.get("priority", "normal"), 2))
    return {"announcements": filtered, "count": len(filtered)}
