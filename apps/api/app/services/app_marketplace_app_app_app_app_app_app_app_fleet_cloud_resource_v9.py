"""Fleet Cloud Resource v9 — track cloud resource utilization and waste."""
from __future__ import annotations
def fleet_cloud_resource_v9(resources: list[dict]) -> dict:
    utilized = [r for r in resources if r.get("utilization_pct", 0) > 20]
    wasted = [r for r in resources if r.get("utilization_pct", 0) <= 20]
    total_cost = sum(r.get("monthly_cost", 0) for r in resources)
    waste_cost = sum(r.get("monthly_cost", 0) for r in wasted)
    return {"resources": len(resources), "utilized": len(utilized), "wasted": len(wasted),
            "total_cost": round(total_cost, 2), "waste_cost": round(waste_cost, 2),
            "healthy": waste_cost < total_cost * 0.1}
