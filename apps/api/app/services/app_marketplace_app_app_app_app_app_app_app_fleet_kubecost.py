"""Fleet Kubecost — track k8s cost monitoring and savings."""
from __future__ import annotations
def fleet_kubecost_status(clusters: list[dict]) -> dict:
    monthly_cost = sum(c.get("monthly_cost_usd", 0) for c in clusters)
    savings_available = sum(c.get("savings_available_usd", 0) for c in clusters)
    return {"clusters": len(clusters), "monthly_cost": round(monthly_cost, 2),
            "savings_available": round(savings_available, 2),
            "savings_pct": round(savings_available / max(monthly_cost, 0.01) * 100, 1)}
