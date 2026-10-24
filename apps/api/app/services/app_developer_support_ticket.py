"""Developer support ticket — track developer support requests."""

from datetime import UTC, datetime
from collections import defaultdict

_tickets: list[dict] = []
PRIORITIES = ["low", "medium", "high", "critical"]


def create_ticket(*, developer_id: str, subject: str, message: str, priority: str = "medium", category: str = "general") -> dict:
    ticket = {
        "id": f"ticket_{len(_tickets) + 1}",
        "developer_id": developer_id, "subject": subject, "message": message,
        "priority": priority if priority in PRIORITIES else "medium",
        "category": category, "status": "open",
        "created_at": datetime.now(UTC).isoformat(),
    }
    _tickets.append(ticket)
    return ticket


def get_open_tickets(developer_id: str) -> list[dict]:
    return [t for t in _tickets if t["developer_id"] == developer_id and t["status"] == "open"]


def get_ticket_stats() -> dict:
    by_priority = defaultdict(int)
    for t in _tickets:
        if t["status"] == "open":
            by_priority[t["priority"]] += 1
    return {"total_open": sum(by_priority.values()), "by_priority": dict(by_priority)}
