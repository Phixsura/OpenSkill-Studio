"""Team activity feed — aggregate team actions into a chronological feed."""
from __future__ import annotations


def build_activity_feed(events: list[dict], *, limit: int = 50,
                         filter_type: str | None = None) -> dict:
    filtered = events if not filter_type else [e for e in events if e.get("type") == filter_type]
    sorted_events = sorted(filtered, key=lambda e: e.get("timestamp", ""), reverse=True)[:limit]
    by_user: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for e in sorted_events:
        user = e.get("user", "unknown")
        etype = e.get("type", "other")
        by_user[user] = by_user.get(user, 0) + 1
        by_type[etype] = by_type.get(etype, 0) + 1
    top_contributor = max(by_user, key=by_user.get) if by_user else None
    items = [{"user": e.get("user", "unknown"), "type": e.get("type", "other"),
              "message": e.get("message", ""), "timestamp": e.get("timestamp", ""),
              "icon": _icon(e.get("type", "other"))} for e in sorted_events]
    return {"total": len(filtered), "shown": len(items), "items": items,
            "by_user": by_user, "by_type": by_type, "top_contributor": top_contributor}


def _icon(t: str) -> str:
    return {"commit": "💻", "deploy": "🚀", "review": "👀", "merge": "🔀",
            "comment": "💬", "issue": "🐛", "release": "📦"}.get(t, "📌")
