"""Cost center — track costs by team, project, and environment."""
from __future__ import annotations


def allocate_by_dimension(costs: list[dict], dimension: str) -> dict:
    by_dim: dict[str, float] = {}
    for c in costs:
        key = c.get(dimension, "unassigned")
        by_dim[key] = round(by_dim.get(key, 0) + c.get("amount", 0), 2)
    total = round(sum(by_dim.values()), 2)
    ranked = sorted(by_dim.items(), key=lambda x: -x[1])
    return {"dimension": dimension, "allocations": dict(ranked), "total": total,
            "top": ranked[0][0] if ranked else None, "groups": len(by_dim)}


def monthly_trend(months: list[dict]) -> dict:
    if len(months) < 2:
        return {"trend": "insufficient_data"}
    latest = months[-1].get("total", 0)
    previous = months[-2].get("total", 0)
    delta = round(latest - previous, 2)
    pct = round(delta / max(previous, 0.01) * 100, 1)
    return {"latest": latest, "previous": previous, "delta": delta,
            "pct_change": pct, "trend": "up" if delta > 0 else "down" if delta < 0 else "flat"}
