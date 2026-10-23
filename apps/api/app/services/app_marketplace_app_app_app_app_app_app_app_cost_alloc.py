"""Cost allocation tracker — allocate costs to teams and projects."""
from __future__ import annotations


def allocate_costs(items: list[dict]) -> dict:
    by_team: dict[str, float] = {}
    by_project: dict[str, float] = {}
    total = 0.0
    for item in items:
        cost = item.get("cost", 0.0)
        total += cost
        team = item.get("team", "unassigned")
        project = item.get("project", "unassigned")
        by_team[team] = round(by_team.get(team, 0) + cost, 2)
        by_project[project] = round(by_project.get(project, 0) + cost, 2)
    top_team = max(by_team, key=by_team.get) if by_team else None
    return {"total_cost": round(total, 2), "by_team": by_team, "by_project": by_project,
            "team_count": len(by_team), "project_count": len(by_project),
            "top_team": top_team, "display": f"${total:,.2f}"}


def compare_periods(current: dict, previous: dict) -> dict:
    cur = current["total_cost"]
    prev = previous["total_cost"]
    delta = round(cur - prev, 2)
    pct_change = round(delta / max(prev, 0.01) * 100, 1)
    trend = "up" if delta > 0 else "down" if delta < 0 else "flat"
    return {"current": cur, "previous": prev, "delta": delta,
            "pct_change": pct_change, "trend": trend}
