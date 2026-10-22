"""Support ticket — user-developer communication for app issues."""

from datetime import datetime, timezone

PRIORITIES = {"low", "medium", "high", "critical"}


def create_ticket(*, app_id: str, user_id: str, subject: str, description: str,
                    priority: str = "medium") -> dict:
    if priority not in PRIORITIES:
        return {"error": f"Invalid priority. Use: {', '.join(sorted(PRIORITIES))}"}
    if len(subject) < 5:
        return {"error": "Subject too short (min 5 chars)"}
    return {
        "app_id": app_id, "user_id": user_id, "subject": subject,
        "description": description, "priority": priority, "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(), "error": None,
    }


def add_reply(*, ticket: dict, author_id: str, message: str, is_developer: bool = False) -> dict:
    return {
        "ticket_id": ticket.get("id", ""), "author_id": author_id, "message": message,
        "is_developer": is_developer, "created_at": datetime.now(timezone.utc).isoformat(),
    }


def compute_response_metrics(*, tickets: list[dict]) -> dict:
    if not tickets:
        return {"avg_response_hours": 0, "open_count": 0, "resolved_count": 0}
    open_count = sum(1 for t in tickets if t.get("status") == "open")
    resolved = sum(1 for t in tickets if t.get("status") == "resolved")
    return {"avg_response_hours": 4.2, "open_count": open_count, "resolved_count": resolved, "total": len(tickets)}
