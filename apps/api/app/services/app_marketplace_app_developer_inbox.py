"""Developer inbox — unified message center for all developer communications."""

from datetime import datetime, timezone
from collections import defaultdict


def create_message(*, from_type: str, subject: str, body: str, priority: str = "normal",
                     app_id: str | None = None) -> dict:
    valid_types = {"system", "review", "support", "team", "marketplace"}
    if from_type not in valid_types:
        return {"error": f"Invalid type. Use: {', '.join(sorted(valid_types))}"}
    return {"from_type": from_type, "subject": subject, "body": body, "priority": priority,
            "app_id": app_id, "read": False, "archived": False,
            "created_at": datetime.now(timezone.utc).isoformat(), "error": None}


def get_inbox_summary(*, messages: list[dict]) -> dict:
    unread = sum(1 for m in messages if not m.get("read"))
    by_type = defaultdict(int)
    for m in messages:
        if not m.get("read"):
            by_type[m.get("from_type", "system")] += 1
    urgent = sum(1 for m in messages if not m.get("read") and m.get("priority") == "urgent")
    return {"total": len(messages), "unread": unread, "urgent": urgent, "by_type": dict(by_type)}


def filter_messages(*, messages: list[dict], type_filter: str | None = None,
                      unread_only: bool = False) -> list[dict]:
    result = messages
    if type_filter:
        result = [m for m in result if m.get("from_type") == type_filter]
    if unread_only:
        result = [m for m in result if not m.get("read")]
    return sorted(result, key=lambda m: m.get("created_at", ""), reverse=True)
