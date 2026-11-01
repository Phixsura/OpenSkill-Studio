"""User segmentation engine — group users by behavior and attributes."""
from __future__ import annotations


def segment_users(users: list[dict], *, rules: list[dict] | None = None) -> dict:
    rules = rules or [
        {"name": "power_users", "field": "actions", "op": "gte", "value": 100},
        {"name": "new_users", "field": "days_since_signup", "op": "lte", "value": 7},
        {"name": "churning", "field": "days_inactive", "op": "gte", "value": 30},
    ]
    segments: dict[str, list[str]] = {r["name"]: [] for r in rules}
    segments["unclassified"] = []
    ops = {"gte": lambda a, b: a >= b, "lte": lambda a, b: a <= b,
           "eq": lambda a, b: a == b, "gt": lambda a, b: a > b, "lt": lambda a, b: a < b}
    for u in users:
        uid = u.get("id", "unknown")
        matched = False
        for r in rules:
            val = u.get(r["field"], 0)
            if ops.get(r["op"], lambda a, b: False)(val, r["value"]):
                segments[r["name"]].append(uid)
                matched = True
        if not matched:
            segments["unclassified"].append(uid)
    total = len(users)
    summary = {k: {"count": len(v), "pct": round(len(v) / max(total, 1) * 100, 1)}
               for k, v in segments.items()}
    return {"total_users": total, "segments": segments, "summary": summary}
