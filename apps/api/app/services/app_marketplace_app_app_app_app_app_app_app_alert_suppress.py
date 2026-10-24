"""Alert suppression rules — silence alerts during known events."""
from __future__ import annotations
import time
import re


_rules: list[dict] = []


def create_rule(name: str, pattern: str, duration_min: int, reason: str) -> dict:
    rule = {"id": len(_rules) + 1, "name": name, "pattern": pattern,
            "start_ts": time.time(), "end_ts": time.time() + duration_min * 60,
            "reason": reason, "suppressed_count": 0, "active": True}
    _rules.append(rule)
    return rule


def should_suppress(alert_name: str, now: float | None = None) -> dict:
    now = now or time.time()
    for rule in _rules:
        if not rule["active"] or now > rule["end_ts"]:
            continue
        if re.search(rule["pattern"], alert_name, re.IGNORECASE):
            rule["suppressed_count"] += 1
            return {"suppress": True, "rule": rule["name"], "reason": rule["reason"]}
    return {"suppress": False}


def suppression_stats() -> dict:
    active = sum(1 for r in _rules if r["active"] and time.time() < r["end_ts"])
    total_suppressed = sum(r["suppressed_count"] for r in _rules)
    return {"total_rules": len(_rules), "active": active,
            "total_suppressed": total_suppressed}


def clear_rules() -> None:
    _rules.clear()
