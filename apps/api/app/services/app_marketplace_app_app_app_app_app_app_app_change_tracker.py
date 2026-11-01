"""Platform change tracker — track all changes across the platform."""
from __future__ import annotations
import time
import html

_changes: list[dict] = []


def record_change(entity: str, action: str, user: str, details: str = "") -> dict:
    entry = {"entity": html.escape(entity), "action": action,
             "user": html.escape(user), "details": html.escape(details),
             "timestamp": time.time(), "id": len(_changes) + 1}
    _changes.append(entry)
    return entry


def get_recent_changes(limit: int = 20, entity: str | None = None) -> dict:
    filtered = _changes if not entity else [c for c in _changes if c["entity"] == entity]
    recent = list(reversed(filtered[-limit:]))
    by_action: dict[str, int] = {}
    for c in filtered:
        by_action[c["action"]] = by_action.get(c["action"], 0) + 1
    return {"changes": recent, "total": len(filtered), "shown": len(recent),
            "by_action": by_action}


def change_frequency(window_hours: int = 24) -> dict:
    cutoff = time.time() - window_hours * 3600
    recent = [c for c in _changes if c["timestamp"] > cutoff]
    return {"window_hours": window_hours, "change_count": len(recent),
            "per_hour": round(len(recent) / max(window_hours, 1), 1)}


def clear_changes() -> None:
    _changes.clear()
