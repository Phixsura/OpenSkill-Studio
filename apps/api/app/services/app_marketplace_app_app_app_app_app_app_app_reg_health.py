"""Service registry health — monitor registered services health status."""
from __future__ import annotations


def registry_health(services: list[dict]) -> dict:
    healthy = [s for s in services if s.get("healthy")]
    stale = [s for s in services if s.get("stale")]
    deregistered = [s for s in services if s.get("deregistered")]
    return {"total": len(services), "healthy": len(healthy),
            "stale": len(stale), "deregistered": len(deregistered),
            "health_pct": round(len(healthy) / max(len(services), 1) * 100, 1)}


def detect_orphans(registered: list[str], deployed: list[str]) -> dict:
    reg_set = set(registered)
    dep_set = set(deployed)
    orphans = sorted(reg_set - dep_set)
    unregistered = sorted(dep_set - reg_set)
    return {"orphans": orphans, "unregistered_deployments": unregistered,
            "clean": len(orphans) == 0 and len(unregistered) == 0}
