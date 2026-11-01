"""Fleet QBR — quarterly business review summary."""
from __future__ import annotations
def fleet_qbr_summary(quarter: dict) -> dict:
    revenue_target = quarter.get("revenue_target", 0)
    revenue_actual = quarter.get("revenue_actual", 0)
    hit = revenue_actual >= revenue_target
    pct = round(revenue_actual / max(revenue_target, 0.01) * 100, 1)
    return {"quarter": quarter.get("name", "Q?"), "target": revenue_target,
            "actual": revenue_actual, "achievement_pct": pct, "target_hit": hit}
