"""Infrastructure cost optimizer — identify cost reduction opportunities."""
from __future__ import annotations


def analyze_resources(resources: list[dict]) -> dict:
    underutilized = []
    oversized = []
    total_cost = 0.0
    potential_savings = 0.0
    for r in resources:
        cost = r.get("monthly_cost", 0)
        utilization = r.get("utilization_pct", 0)
        total_cost += cost
        if utilization < 20:
            saving = cost * 0.7  # can save 70%
            potential_savings += saving
            underutilized.append({**r, "suggestion": "downsize_or_remove", "saving": round(saving, 2)})
        elif utilization < 50:
            saving = cost * 0.3
            potential_savings += saving
            oversized.append({**r, "suggestion": "rightsize", "saving": round(saving, 2)})
    return {"total_cost": round(total_cost, 2), "potential_savings": round(potential_savings, 2),
            "savings_pct": round(potential_savings / max(total_cost, 0.01) * 100, 1),
            "underutilized": underutilized, "oversized": oversized,
            "recommendations": len(underutilized) + len(oversized)}


def projected_savings(monthly_savings: float, months: int = 12) -> dict:
    annual = round(monthly_savings * months, 2)
    return {"monthly": monthly_savings, "annual": annual,
            "display_monthly": f"${monthly_savings:,.2f}",
            "display_annual": f"${annual:,.2f}"}
