"""Fleet pod anti-affinity — check HA deployment spread."""
from __future__ import annotations
def fleet_antiaffinity(deployments: list[dict]) -> dict:
    with_aa = [d for d in deployments if d.get("has_anti_affinity", False)]
    colocated = [d for d in deployments if d.get("all_same_node", False)]
    return {"total": len(deployments), "with_anti_affinity": len(with_aa),
            "colocated_risk": len(colocated), "ha_compliant": len(colocated) == 0}
