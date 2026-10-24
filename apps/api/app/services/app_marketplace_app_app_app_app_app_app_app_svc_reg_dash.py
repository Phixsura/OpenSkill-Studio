"""Service registry dashboard — unified view of all registered services."""
from __future__ import annotations


def build_registry_dashboard(services: list[dict]) -> dict:
    total = len(services)
    healthy = sum(1 for s in services if s.get("status") == "healthy")
    by_team: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for s in services:
        by_team[s.get("team", "unassigned")] = by_team.get(s.get("team", "unassigned"), 0) + 1
        by_type[s.get("type", "service")] = by_type.get(s.get("type", "service"), 0) + 1
    return {"total": total, "healthy": healthy, "unhealthy": total - healthy,
            "health_pct": round(healthy / max(total, 1) * 100),
            "by_team": by_team, "by_type": by_type,
            "teams": sorted(by_team.keys()), "types": sorted(by_type.keys())}
