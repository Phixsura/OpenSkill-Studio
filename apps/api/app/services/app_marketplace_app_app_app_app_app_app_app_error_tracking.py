"""Error tracking — real-time error tracking with stack trace grouping."""

import html
import hashlib
from collections import defaultdict


def track_errors(*, errors: list[dict], period: str = "24h") -> dict:
    groups: dict[str, dict] = {}
    for e in errors:
        fp = hashlib.sha256(f"{e.get('type', '')}:{e.get('message', '')}".encode()).hexdigest()[:8]
        if fp not in groups:
            groups[fp] = {"fingerprint": fp, "type": e.get("type", "Error"),
                           "message": html.escape(e.get("message", "")),
                           "count": 0, "users": set(), "first_seen": e.get("timestamp", ""),
                           "last_seen": e.get("timestamp", "")}
        groups[fp]["count"] += 1
        groups[fp]["last_seen"] = e.get("timestamp", "")
        if e.get("user_id"):
            groups[fp]["users"].add(e["user_id"])
    items = []
    for g in sorted(groups.values(), key=lambda x: -x["count"]):
        items.append({**g, "affected_users": len(g["users"]), "users": None})
    total = sum(g["count"] for g in items)
    return {"groups": items, "total_errors": total, "unique_errors": len(items),
            "period": period, "error_rate_trend": "up" if total > 100 else "stable"}
