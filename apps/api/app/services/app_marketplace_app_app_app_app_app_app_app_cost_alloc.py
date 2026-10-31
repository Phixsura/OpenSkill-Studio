"""Cost allocation tracker — allocate infrastructure costs to teams/services."""
from __future__ import annotations
from collections import defaultdict


def allocate_costs(resources: list[dict]) -> dict:
    by_team: dict[str, float] = defaultdict(float)
    by_service: dict[str, float] = defaultdict(float)
    total = 0.0
    for r in resources:
        cost = r.get("monthly_cost", 0)
        total += cost
        by_team[r.get("team", "unassigned")] += cost
        by_service[r.get("service", "shared")] += cost
    teams = [{"team": k, "cost": round(v, 2), "pct": round(v / max(total, 0.01) * 100, 1)}
             for k, v in sorted(by_team.items(), key=lambda x: -x[1])]
    services = [{"service": k, "cost": round(v, 2), "pct": round(v / max(total, 0.01) * 100, 1)}
                for k, v in sorted(by_service.items(), key=lambda x: -x[1])]
    return {"total_cost": round(total, 2), "by_team": teams,
            "by_service": services, "resources": len(resources)}


def budget_vs_actual(budget: float, actual: float) -> dict:
    variance = round(actual - budget, 2)
    variance_pct = round(variance / max(budget, 0.01) * 100, 1)
    status = "under" if actual <= budget else ("warning" if actual <= budget * 1.1 else "over")
    return {"budget": budget, "actual": actual, "variance": variance,
            "variance_pct": variance_pct, "status": status}
