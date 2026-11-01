"""Response time budget tracker — track how much of the latency budget is used."""
from __future__ import annotations


def track_budget(endpoint: str, budget_ms: float, stages: list[dict]) -> dict:
    total_used = sum(s.get("duration_ms", 0) for s in stages)
    remaining = max(0, budget_ms - total_used)
    pct_used = round(total_used / max(budget_ms, 0.01) * 100, 1)
    over_budget = total_used > budget_ms
    stage_breakdown = [{"name": s["name"], "ms": s["duration_ms"],
                        "pct": round(s["duration_ms"] / max(budget_ms, 0.01) * 100, 1)}
                       for s in stages]
    return {"endpoint": endpoint, "budget_ms": budget_ms, "used_ms": round(total_used, 1),
            "remaining_ms": round(remaining, 1), "pct_used": pct_used,
            "over_budget": over_budget, "stages": stage_breakdown}
