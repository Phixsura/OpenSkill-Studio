"""Support ticket — create, update, and manage support tickets."""

import secrets
from datetime import datetime


PRIORITIES = {"low": 1, "medium": 2, "high": 3, "critical": 4}
STATUSES = {"open", "in_progress", "waiting", "resolved", "closed"}


def create_ticket(*, subject: str, description: str, priority: str = "medium",
                    reporter_id: str, app_id: str | None = None) -> dict:
    if len(subject) < 5:
        return {"error": "Subject must be at least 5 characters"}
    if priority not in PRIORITIES:
        return {"error": f"Invalid priority. Valid: {', '.join(PRIORITIES)}"}
    ticket_id = f"TKT-{secrets.token_hex(4).upper()}"
    return {
        "ticket_id": ticket_id,
        "subject": subject,
        "description": description,
        "priority": priority,
        "priority_level": PRIORITIES[priority],
        "status": "open",
        "reporter_id": reporter_id,
        "app_id": app_id,
        "created_at": datetime.utcnow().isoformat(),
    }


def update_ticket_status(*, ticket_id: str, new_status: str,
                           note: str | None = None) -> dict:
    if new_status not in STATUSES:
        return {"error": f"Invalid status. Valid: {', '.join(sorted(STATUSES))}"}
    return {"ticket_id": ticket_id, "status": new_status,
            "note": note, "updated": True}


def get_ticket_stats(*, tickets: list[dict]) -> dict:
    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    for t in tickets:
        by_status[t.get("status", "open")] = by_status.get(t.get("status", "open"), 0) + 1
        by_priority[t.get("priority", "medium")] = by_priority.get(t.get("priority", "medium"), 0) + 1
    return {"total": len(tickets), "by_status": by_status, "by_priority": by_priority,
            "open_count": by_status.get("open", 0) + by_status.get("in_progress", 0)}
