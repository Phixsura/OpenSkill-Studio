"""Infrastructure cost optimizer — identify cost savings opportunities."""
from __future__ import annotations


def analyze_resources(resources: list[dict]) -> dict:
    savings = []
    total_monthly = 0
    potential_savings = 0
    for r in resources:
        cost = r.get("monthly_cost", 0)
        total_monthly += cost
        utilization = r.get("utilization_pct", 100)
        if utilization < 20:
            save = round(cost * 0.7, 2)
            savings.append({"resource": r["name"], "type": r.get("type", "unknown"),
                            "utilization_pct": utilization, "monthly_cost": cost,
                            "potential_savings": save, "recommendation": "terminate_or_downsize"})
            potential_savings += save
        elif utilization < 50:
            save = round(cost * 0.4, 2)
            savings.append({"resource": r["name"], "type": r.get("type", "unknown"),
                            "utilization_pct": utilization, "monthly_cost": cost,
                            "potential_savings": save, "recommendation": "rightsize"})
            potential_savings += save
    savings.sort(key=lambda s: -s["potential_savings"])
    return {"total_monthly_cost": round(total_monthly, 2),
            "potential_savings": round(potential_savings, 2),
            "savings_pct": round(potential_savings / max(total_monthly, 0.01) * 100, 1),
            "opportunities": savings, "resources_analyzed": len(resources)}


def reserved_vs_ondemand(instances: list[dict]) -> dict:
    reserved = sum(1 for i in instances if i.get("pricing") == "reserved")
    ondemand = sum(1 for i in instances if i.get("pricing") == "on_demand")
    reserved_cost = sum(i.get("monthly_cost", 0) for i in instances if i.get("pricing") == "reserved")
    ondemand_cost = sum(i.get("monthly_cost", 0) for i in instances if i.get("pricing") == "on_demand")
    return {"reserved": reserved, "on_demand": ondemand,
            "reserved_cost": round(reserved_cost, 2),
            "on_demand_cost": round(ondemand_cost, 2),
            "recommendation": "increase_reserved" if ondemand > reserved else "balanced"}
