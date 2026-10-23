"""Usage analytics — aggregate app usage metrics over time."""
from __future__ import annotations


def aggregate_usage(events: list[dict]) -> dict:
    by_action: dict[str, int] = {}
    by_day: dict[str, int] = {}
    unique_users: set[str] = set()
    for e in events:
        action = e.get("action", "unknown")
        by_action[action] = by_action.get(action, 0) + 1
        day = e.get("date", "unknown")
        by_day[day] = by_day.get(day, 0) + 1
        if uid := e.get("user_id"):
            unique_users.add(uid)
    total = len(events)
    top_action = max(by_action, key=by_action.get) if by_action else None
    peak_day = max(by_day, key=by_day.get) if by_day else None
    return {"total_events": total, "unique_users": len(unique_users),
            "by_action": dict(sorted(by_action.items(), key=lambda x: -x[1])),
            "by_day": by_day, "top_action": top_action, "peak_day": peak_day,
            "avg_per_day": round(total / max(len(by_day), 1), 1)}
