"""Dependency health — monitor third-party dependency health."""
from __future__ import annotations


def check_dependency_health(deps: list[dict]) -> dict:
    healthy = 0
    degraded = 0
    down = 0
    for d in deps:
        status = d.get("status", "unknown")
        if status == "healthy":
            healthy += 1
        elif status == "degraded":
            degraded += 1
        else:
            down += 1
    total = len(deps)
    return {"total": total, "healthy": healthy, "degraded": degraded, "down": down,
            "health_pct": round(healthy / max(total, 1) * 100),
            "all_healthy": healthy == total}


def suggest_alternatives(dep: dict) -> dict:
    alternatives = {
        "redis": ["memcached", "dragonfly"],
        "postgres": ["cockroachdb", "yugabytedb"],
        "elasticsearch": ["opensearch", "meilisearch"],
    }
    name = dep.get("name", "").lower()
    alts = alternatives.get(name, [])
    return {"dependency": dep.get("name", ""), "alternatives": alts,
            "has_alternatives": len(alts) > 0}
