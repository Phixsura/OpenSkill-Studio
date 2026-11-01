"""Resource optimizer — identify and optimize resource allocation."""
from __future__ import annotations


def analyze_waste(resources: list[dict]) -> dict:
    wasted = []
    total_waste_cost = 0
    for r in resources:
        usage = r.get("usage_pct", 0)
        cost = r.get("monthly_cost", 0)
        if usage < 10:
            waste = round(cost * 0.9, 2)
            wasted.append({"name": r["name"], "usage_pct": usage, "cost": cost,
                            "wasted_cost": waste, "action": "terminate_or_downsize"})
            total_waste_cost += waste
        elif usage < 30:
            waste = round(cost * 0.5, 2)
            wasted.append({"name": r["name"], "usage_pct": usage, "cost": cost,
                            "wasted_cost": waste, "action": "rightsize"})
            total_waste_cost += waste
    return {"wasted_resources": wasted, "waste_count": len(wasted),
            "total_waste_cost": round(total_waste_cost, 2),
            "display": f"${total_waste_cost:,.2f}/mo"}


def optimization_plan(waste: dict) -> dict:
    actions = waste["wasted_resources"]
    immediate = [a for a in actions if a["action"] == "terminate_or_downsize"]
    scheduled = [a for a in actions if a["action"] == "rightsize"]
    return {"immediate_actions": len(immediate), "scheduled_actions": len(scheduled),
            "total_actions": len(actions), "potential_savings": waste["total_waste_cost"]}
