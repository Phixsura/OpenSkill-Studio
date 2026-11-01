"""Fleet conversion funnel — track signup to activation funnel."""
from __future__ import annotations
def fleet_conversion_funnel(steps: list[dict]) -> dict:
    if not steps:
        return {"steps": 0, "overall_rate": 0}
    first = steps[0].get("count", 1)
    last = steps[-1].get("count", 0)
    overall = round(last / max(first, 1) * 100, 1)
    drop_offs = [{"step": steps[i].get("name", f"step_{i}"),
                  "drop_pct": round((1 - steps[i+1].get("count", 0) / max(steps[i].get("count", 1), 1)) * 100, 1)}
                 for i in range(len(steps) - 1)]
    worst = max(drop_offs, key=lambda d: d["drop_pct"]) if drop_offs else None
    return {"steps": len(steps), "overall_rate": overall,
            "worst_drop": worst, "healthy": overall >= 20}
