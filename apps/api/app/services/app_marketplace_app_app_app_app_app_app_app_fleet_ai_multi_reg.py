"""Fleet AI Multi-Region — track global AI deployment across regions."""
from __future__ import annotations
def fleet_ai_multi_region(deployments: list[dict]) -> dict:
    active = [d for d in deployments if d.get("active", True)]
    regions = set()
    for d in deployments:
        regions.update(d.get("regions", []))
    total_rps = sum(d.get("rps", 0) for d in deployments)
    failover_tested = all(d.get("failover_ok", False) for d in deployments)
    return {"deployments": len(deployments), "active": len(active), "regions": len(regions),
            "rps": total_rps, "failover_ok": failover_tested, "global": len(regions) > 3}
