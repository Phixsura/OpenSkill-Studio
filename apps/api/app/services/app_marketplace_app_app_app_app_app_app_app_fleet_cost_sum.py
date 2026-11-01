"""Fleet cost summary — total cost across the service fleet."""
from __future__ import annotations
def fleet_cost_summary(services: list[dict]) -> dict:
    total = sum(s.get("cost", 0) for s in services)
    avg = round(total / max(len(services), 1), 2)
    return {"total_cost": round(total, 2), "avg_cost": avg, "services": len(services)}
