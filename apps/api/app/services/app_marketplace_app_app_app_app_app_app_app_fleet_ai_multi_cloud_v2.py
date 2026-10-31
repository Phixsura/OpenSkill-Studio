"""Fleet AI Multi-Cloud v2 — track cross-cloud AI deployment management."""
from __future__ import annotations
def fleet_ai_multi_cloud_v2(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    clouds = set()
    for m in managers:
        clouds.update(m.get("clouds", []))
    deployments = sum(m.get("deployments", 0) for m in managers)
    failover_tested = all(m.get("failover_ok", False) for m in managers)
    return {"managers": len(managers), "active": len(active), "clouds": sorted(clouds),
            "deployments": deployments, "failover_ok": failover_tested, "multi_cloud": len(clouds) > 2}
