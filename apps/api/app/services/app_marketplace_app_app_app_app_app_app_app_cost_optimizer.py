"""Infrastructure cost optimizer — identify savings across cloud resources."""
from __future__ import annotations


def analyze_cost_savings(resources: list[dict]) -> dict:
    recommendations = []
    total_current = 0.0
    total_savings = 0.0
    for r in resources:
        cost = r.get("monthly_cost", 0)
        utilization = r.get("utilization_pct", 100)
        total_current += cost
        if utilization < 20 and cost > 50:
            savings = cost * 0.7
            recommendations.append({
                "resource": r["name"], "type": r.get("type", ""),
                "action": "terminate", "reason": "Under 20% utilization",
                "current_cost": cost, "savings": round(savings, 2),
            })
            total_savings += savings
        elif utilization < 50 and cost > 100:
            savings = cost * 0.4
            recommendations.append({
                "resource": r["name"], "type": r.get("type", ""),
                "action": "downsize", "reason": f"Only {utilization}% utilized",
                "current_cost": cost, "savings": round(savings, 2),
            })
            total_savings += savings
        elif r.get("reserved", False) is False and cost > 200:
            savings = cost * 0.3
            recommendations.append({
                "resource": r["name"], "type": r.get("type", ""),
                "action": "reserve", "reason": "Switch to reserved pricing",
                "current_cost": cost, "savings": round(savings, 2),
            })
            total_savings += savings
    recommendations.sort(key=lambda x: -x["savings"])
    return {
        "total_monthly_cost": round(total_current, 2),
        "total_display": f"${total_current:,.0f}/mo",
        "potential_savings": round(total_savings, 2),
        "savings_display": f"${total_savings:,.0f}/mo",
        "savings_pct": round(total_savings / max(total_current, 1) * 100),
        "recommendations": recommendations,
        "count": len(recommendations),
    }
