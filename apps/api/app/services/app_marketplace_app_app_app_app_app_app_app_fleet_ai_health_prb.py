"""Fleet AI Health Probe v2 — track deep health checking with dependencies."""
from __future__ import annotations
def fleet_ai_health_probe_v2(probes: list[dict]) -> dict:
    active = [p for p in probes if p.get("active", True)]
    endpoints = sum(p.get("endpoints", 0) for p in probes)
    checks_24h = sum(p.get("checks_24h", 0) for p in probes)
    deps_checked = sum(p.get("deps", 0) for p in probes)
    all_healthy = all(p.get("healthy", False) for p in probes)
    return {"probes": len(probes), "active": len(active), "endpoints": endpoints,
            "checks_24h": checks_24h, "deps": deps_checked, "all_healthy": all_healthy}
