"""User activity feed — generate personalized activity feeds."""
from __future__ import annotations
import html
import time

_activities: list[dict] = []


def add_activity(actor: str, action: str, target: str, metadata: dict | None = None) -> dict:
    entry = {"actor": html.escape(actor), "action": action,
             "target": html.escape(target), "metadata": metadata or {},
             "timestamp": time.time()}
    _activities.append(entry)
    return entry


def get_feed(limit: int = 20, actor: str | None = None) -> dict:
    items = _activities if not actor else [a for a in _activities if a["actor"] == actor]
    feed = list(reversed(items[-limit:]))
    actions: dict[str, int] = {}
    for a in feed:
        actions[a["action"]] = actions.get(a["action"], 0) + 1
    return {"items": feed, "count": len(feed), "total": len(items), "by_action": actions}


def clear_activities() -> None:
    _activities.clear()
