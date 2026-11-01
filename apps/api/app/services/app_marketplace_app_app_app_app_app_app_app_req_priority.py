"""Request priority classifier — classify incoming requests by priority."""
from __future__ import annotations


def classify_priority(request: dict, rules: list[dict]) -> dict:
    for rule in rules:
        match = True
        for cond in rule.get("conditions", []):
            actual = request.get(cond["field"])
            if cond["op"] == "eq" and actual != cond["value"]:
                match = False
            elif cond["op"] == "contains" and (actual is None or cond["value"] not in str(actual)):
                match = False
            elif cond["op"] == "in" and actual not in cond["value"]:
                match = False
        if match:
            return {"priority": rule["priority"], "rule": rule["name"], "matched": True}
    return {"priority": "normal", "rule": "default", "matched": False}


def priority_stats(requests: list[dict]) -> dict:
    by_priority: dict[str, int] = {}
    for r in requests:
        p = r.get("priority", "normal")
        by_priority[p] = by_priority.get(p, 0) + 1
    return {"total": len(requests), "by_priority": by_priority}
