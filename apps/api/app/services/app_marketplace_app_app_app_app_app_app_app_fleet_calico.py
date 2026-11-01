"""Fleet Calico — track Calico networking and policy."""
from __future__ import annotations
def fleet_calico_status(nodes: list[dict]) -> dict:
    healthy = [n for n in nodes if n.get("felix_ready", True)]
    policies = sum(n.get("network_policies", 0) for n in nodes)
    return {"nodes": len(nodes), "healthy": len(healthy),
            "total_policies": policies, "all_healthy": len(healthy) == len(nodes)}
