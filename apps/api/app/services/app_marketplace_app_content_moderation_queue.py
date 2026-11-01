"""Content moderation queue — process flagged content for review."""

import secrets
from datetime import datetime


CONTENT_TYPES = {"review", "app_listing", "profile", "comment", "screenshot"}
ACTIONS = {"approve", "reject", "escalate"}


def add_to_queue(*, content_type: str, content_id: str, reason: str,
                   reported_by: str) -> dict:
    if content_type not in CONTENT_TYPES:
        return {"error": f"Invalid type. Valid: {', '.join(sorted(CONTENT_TYPES))}"}
    return {
        "queue_id": f"mod_{secrets.token_urlsafe(8)}",
        "content_type": content_type,
        "content_id": content_id,
        "reason": reason,
        "reported_by": reported_by,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
    }


def process_item(*, queue_id: str, action: str, moderator: str,
                   note: str | None = None) -> dict:
    if action not in ACTIONS:
        return {"error": f"Invalid action. Valid: {', '.join(sorted(ACTIONS))}"}
    return {
        "queue_id": queue_id,
        "action": action,
        "moderator": moderator,
        "note": note,
        "processed_at": datetime.utcnow().isoformat(),
    }


def get_queue_stats(*, items: list[dict]) -> dict:
    pending = sum(1 for i in items if i.get("status") == "pending")
    by_type: dict[str, int] = {}
    for i in items:
        ct = i.get("content_type", "unknown")
        by_type[ct] = by_type.get(ct, 0) + 1
    return {"total": len(items), "pending": pending,
            "processed": len(items) - pending, "by_type": by_type}
