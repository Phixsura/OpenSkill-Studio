"""Content scheduler — schedule content publication at specific times."""

import secrets
from datetime import datetime


CONTENT_TYPES = {"blog_post", "changelog", "announcement", "newsletter", "release"}


def schedule_content(*, content_type: str, title: str, body: str,
                       publish_at: str, author: str) -> dict:
    if content_type not in CONTENT_TYPES:
        return {"error": f"Invalid type. Valid: {', '.join(sorted(CONTENT_TYPES))}"}
    try:
        target = datetime.fromisoformat(publish_at)
    except ValueError:
        return {"error": "Invalid date format"}
    now = datetime.utcnow()
    if target <= now:
        return {"error": "Publish date must be in the future"}
    return {
        "schedule_id": f"sched_{secrets.token_urlsafe(8)}",
        "content_type": content_type,
        "title": title,
        "author": author,
        "publish_at": publish_at,
        "status": "scheduled",
        "created_at": now.isoformat(),
    }


def get_schedule_calendar(*, items: list[dict]) -> dict:
    by_date: dict[str, list] = {}
    for item in items:
        date = item.get("publish_at", "")[:10]
        by_date.setdefault(date, []).append(item)
    return {"dates": dict(sorted(by_date.items())),
            "total_scheduled": len(items), "unique_dates": len(by_date)}
