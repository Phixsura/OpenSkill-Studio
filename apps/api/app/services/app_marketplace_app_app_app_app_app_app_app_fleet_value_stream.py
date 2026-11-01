"""Fleet value stream — track end-to-end value delivery."""
from __future__ import annotations
def fleet_value_stream(stages: list[dict]) -> dict:
    total_time = sum(s.get("cycle_time_hours", 0) for s in stages)
    value_time = sum(s.get("value_add_hours", 0) for s in stages)
    efficiency = round(value_time / max(total_time, 0.01) * 100, 1)
    bottleneck = max(stages, key=lambda s: s.get("wait_time_hours", 0)) if stages else None
    return {"stages": len(stages), "total_cycle_hours": total_time,
            "efficiency_pct": efficiency, "bottleneck": bottleneck.get("name") if bottleneck else None}
