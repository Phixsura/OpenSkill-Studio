"""Fleet log volume — track logging volume and costs."""
from __future__ import annotations
def fleet_log_volume(sources: list[dict]) -> dict:
    total_gb = sum(s.get("gb_per_day", 0) for s in sources)
    cost = round(total_gb * 0.50, 2)  # $0.50/GB
    return {"total_gb_per_day": round(total_gb, 1), "daily_cost": cost,
            "sources": len(sources), "expensive": cost > 100}
