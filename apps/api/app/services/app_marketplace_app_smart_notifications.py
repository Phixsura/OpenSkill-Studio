"""Smart notifications — intelligent notification routing and batching."""

from collections import defaultdict


def should_notify_immediately(*, event_type: str, severity: str) -> bool:
    immediate = {"security_alert", "app_suspended", "payment_failed", "data_breach"}
    return event_type in immediate or severity == "critical"


def batch_notifications(*, notifications: list[dict], window_minutes: int = 15) -> list[dict]:
    groups: dict[str, list] = defaultdict(list)
    for n in notifications:
        key = n.get("category", "general")
        groups[key].append(n)
    batches = []
    for category, items in groups.items():
        if len(items) == 1:
            batches.append(items[0])
        else:
            batches.append({"type": "batch", "category": category, "count": len(items),
                            "summary": f"{len(items)} {category} notifications", "items": items})
    return batches


def compute_notification_digest(*, notifications: list[dict]) -> dict:
    by_type = defaultdict(int)
    for n in notifications:
        by_type[n.get("type", "info")] += 1
    return {"total": len(notifications), "by_type": dict(by_type),
            "has_urgent": any(n.get("severity") == "critical" for n in notifications)}
