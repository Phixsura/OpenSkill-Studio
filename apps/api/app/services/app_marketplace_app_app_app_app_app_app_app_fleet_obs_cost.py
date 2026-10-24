"""Fleet observability cost — track monitoring/logging costs."""
from __future__ import annotations
def fleet_obs_cost(components: list[dict]) -> dict:
    total = sum(c.get("monthly_cost", 0) for c in components)
    by_type: dict[str, float] = {}
    for c in components:
        t = c.get("type", "other")
        by_type[t] = by_type.get(t, 0) + c.get("monthly_cost", 0)
    return {"total_monthly": round(total, 2), "by_type": by_type, "expensive": total > 10000}
