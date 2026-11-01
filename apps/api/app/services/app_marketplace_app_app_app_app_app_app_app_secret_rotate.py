"""Secret rotation scheduler — track and schedule secret/key rotations."""
from __future__ import annotations
import time


def check_rotation(secrets: list[dict], max_age_days: int = 90) -> dict:
    now = time.time()
    results = []
    for s in secrets:
        age_days = round((now - s["created_at"]) / 86400, 1)
        overdue = age_days > max_age_days
        days_until = round(max_age_days - age_days, 1)
        results.append({"name": s["name"], "age_days": age_days,
                        "overdue": overdue, "days_until_rotation": max(0, days_until),
                        "type": s.get("type", "generic")})
    overdue_count = sum(1 for r in results if r["overdue"])
    return {"secrets": results, "total": len(results), "overdue": overdue_count,
            "healthy": len(results) - overdue_count, "max_age_days": max_age_days}


def rotation_plan(overdue_secrets: list[dict]) -> list[dict]:
    sorted_s = sorted(overdue_secrets, key=lambda s: -s["age_days"])
    plan = []
    for i, s in enumerate(sorted_s):
        plan.append({"priority": i + 1, "name": s["name"],
                      "age_days": s["age_days"], "action": "rotate_immediately"})
    return plan
