"""Cost optimizer — identify savings opportunities for app infrastructure."""


def analyze_costs(*, resources: list[dict]) -> dict:
    total_monthly = sum(r.get("monthly_cost", 0) for r in resources)
    recommendations = []
    for r in resources:
        util = r.get("utilization_pct", 100)
        cost = r.get("monthly_cost", 0)
        if util < 20 and cost > 0:
            savings = round(cost * 0.7, 2)
            recommendations.append({
                "resource": r["name"], "type": "downsize",
                "reason": f"Low utilization ({util}%)",
                "potential_savings": savings, "priority": "high",
            })
        elif util < 50 and cost > 10:
            savings = round(cost * 0.4, 2)
            recommendations.append({
                "resource": r["name"], "type": "rightsize",
                "reason": f"Moderate utilization ({util}%)",
                "potential_savings": savings, "priority": "medium",
            })
        if r.get("reserved", False) and cost > 50:
            savings = round(cost * 0.3, 2)
            recommendations.append({
                "resource": r["name"], "type": "reserved_pricing",
                "reason": "Switch to reserved pricing",
                "potential_savings": savings, "priority": "low",
            })
    total_savings = round(sum(rec["potential_savings"] for rec in recommendations), 2)
    return {
        "total_monthly_cost": round(total_monthly, 2),
        "recommendations": recommendations,
        "total_potential_savings": total_savings,
        "savings_pct": round(total_savings / max(total_monthly, 0.01) * 100, 1),
    }
