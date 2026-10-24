"""API latency budget — allocate and track latency budgets per endpoint."""
from __future__ import annotations


def allocate_budget(total_ms: float, stages: list[dict]) -> dict:
    allocated = []
    remaining = total_ms
    for stage in stages:
        budget = stage.get("budget_ms", 0)
        allocated.append({"stage": stage["name"], "budget_ms": budget,
                          "pct": round(budget / max(total_ms, 0.01) * 100, 1)})
        remaining -= budget
    return {"total_ms": total_ms, "stages": allocated,
            "remaining_ms": round(remaining, 1),
            "fully_allocated": remaining <= 0}


def check_budget(endpoint: str, budget_ms: float, actual_ms: float) -> dict:
    within = actual_ms <= budget_ms
    overshoot = round(max(0, actual_ms - budget_ms), 1)
    pct_used = round(actual_ms / max(budget_ms, 0.01) * 100, 1)
    return {"endpoint": endpoint, "budget_ms": budget_ms, "actual_ms": actual_ms,
            "within_budget": within, "overshoot_ms": overshoot, "pct_used": pct_used}
