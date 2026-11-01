"""Error budget dashboard — unified view of all error budgets."""
from __future__ import annotations


def build_error_budget_dashboard(slos: list[dict]) -> dict:
    budgets = []
    total_remaining = 0
    exhausted_count = 0
    for slo in slos:
        target = slo.get("target_pct", 99.9)
        actual = slo.get("actual_pct", 100)
        budget_total = 100 - target
        consumed = max(0, target - actual)
        consumed_pct = round(consumed / max(budget_total, 0.001) * 100, 1)
        remaining_pct = max(0, round(100 - consumed_pct, 1))
        exhausted = consumed_pct >= 100
        if exhausted:
            exhausted_count += 1
        total_remaining += remaining_pct
        budgets.append({"name": slo["name"], "target": target, "actual": actual,
                         "consumed_pct": consumed_pct, "remaining_pct": remaining_pct,
                         "exhausted": exhausted})
    avg_remaining = round(total_remaining / max(len(slos), 1), 1)
    return {"budgets": budgets, "total_slos": len(slos), "exhausted": exhausted_count,
            "avg_remaining_pct": avg_remaining,
            "status": "critical" if exhausted_count > 0 else "healthy"}
