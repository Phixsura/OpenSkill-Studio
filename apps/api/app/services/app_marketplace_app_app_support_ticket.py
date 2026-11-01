"""Support ticket — help desk ticket management."""

import html
import secrets
from datetime import datetime, timezone

PRIORITIES = {"low": 1, "medium": 2, "high": 3, "urgent": 4}
STATUSES = ["open", "in_progress", "waiting", "resolved", "closed"]


def create_ticket(*, subject: str, body: str, priority: str = "medium",
                    category: str = "general", user_email: str = "") -> dict:
    return {
        "id": f"TKT-{secrets.token_hex(4).upper()}",
        "subject": html.escape(subject),
        "body": html.escape(body),
        "priority": priority,
        "priority_level": PRIORITIES.get(priority, 2),
        "category": category,
        "status": "open",
        "user_email": user_email,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_ticket_queue(*, tickets: list[dict]) -> dict:
    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    for t in tickets:
        by_status[t.get("status", "open")] = by_status.get(t.get("status", "open"), 0) + 1
        by_priority[t.get("priority", "medium")] = by_priority.get(t.get("priority", "medium"), 0) + 1
    open_count = sum(v for k, v in by_status.items() if k not in ("resolved", "closed"))
    return {"total": len(tickets), "open": open_count,
            "by_status": by_status, "by_priority": by_priority,
            "has_urgent": by_priority.get("urgent", 0) > 0}
