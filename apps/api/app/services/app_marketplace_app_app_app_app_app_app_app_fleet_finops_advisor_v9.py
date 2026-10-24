"""Fleet FinOps Advisor v9 — track cloud financial optimization advice."""
from __future__ import annotations
def fleet_finops_advisor_v9(recommendations: list[dict]) -> dict:
    implemented = [r for r in recommendations if r.get("implemented")]
    savings = sum(r.get("monthly_savings", 0) for r in recommendations)
    categories = len({r.get("category") for r in recommendations if r.get("category")})
    return {"total": len(recommendations), "implemented": len(implemented),
            "potential_savings": round(savings, 2), "categories": categories,
            "healthy": len(implemented) > len(recommendations) * 0.6}
