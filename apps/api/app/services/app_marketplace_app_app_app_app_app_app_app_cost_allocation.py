"""Cost allocation tracker — attribute infrastructure costs to teams/services."""
from __future__ import annotations


def allocate_costs(items: list[dict]) -> dict:
    by_team: dict[str, float] = {}
    by_service: dict[str, float] = {}
    total = 0.0
    for item in items:
        cost = item.get("cost", 0)
        team = item.get("team", "unassigned")
        service = item.get("service", "other")
        by_team[team] = by_team.get(team, 0) + cost
        by_service[service] = by_service.get(service, 0) + cost
        total += cost
    teams = [{"team": k, "cost": round(v, 2), "pct": round(v / max(total, 0.01) * 100, 1),
              "display": f"${v:,.2f}"} for k, v in sorted(by_team.items(), key=lambda x: -x[1])]
    services = [{"service": k, "cost": round(v, 2), "pct": round(v / max(total, 0.01) * 100, 1),
                 "display": f"${v:,.2f}"} for k, v in sorted(by_service.items(), key=lambda x: -x[1])]
    return {"total": round(total, 2), "total_display": f"${total:,.2f}",
            "by_team": teams, "by_service": services,
            "top_spender": teams[0]["team"] if teams else None}
