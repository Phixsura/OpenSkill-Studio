"""Resource rightsizing advisor — recommend optimal resource allocations."""
from __future__ import annotations


def analyze_rightsizing(resources: list[dict]) -> dict:
    recommendations = []
    total_savings = 0
    for r in resources:
        cpu_pct = r.get("cpu_avg_pct", 0)
        mem_pct = r.get("mem_avg_pct", 0)
        cost = r.get("monthly_cost", 0)
        if cpu_pct < 20 and mem_pct < 20:
            savings = round(cost * 0.6, 2)
            recommendations.append({**r, "action": "downsize_2x", "savings": savings})
        elif cpu_pct < 40 and mem_pct < 40:
            savings = round(cost * 0.3, 2)
            recommendations.append({**r, "action": "downsize_1x", "savings": savings})
        total_savings += recommendations[-1]["savings"] if recommendations and recommendations[-1].get("name") == r.get("name") else 0
    total_savings = round(sum(r["savings"] for r in recommendations), 2)
    return {"recommendations": recommendations, "count": len(recommendations),
            "total_savings": total_savings, "display": f"${total_savings:,.2f}/mo"}
