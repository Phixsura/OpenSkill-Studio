"""Dependency staleness checker — detect outdated service dependencies."""
from __future__ import annotations


def check_staleness(dependencies: list[dict], max_age_days: int = 180) -> dict:
    stale = []
    current = []
    for dep in dependencies:
        age = dep.get("age_days", 0)
        if age > max_age_days:
            stale.append({"name": dep["name"], "current_version": dep.get("version", ""),
                           "latest_version": dep.get("latest", ""),
                           "age_days": age, "overdue_by": age - max_age_days})
        else:
            current.append(dep["name"])
    stale.sort(key=lambda s: -s["age_days"])
    return {"stale": stale, "current": len(current), "stale_count": len(stale),
            "total": len(dependencies), "max_age_days": max_age_days,
            "staleness_pct": round(len(stale) / max(len(dependencies), 1) * 100, 1)}
