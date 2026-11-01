"""Fleet Container Network v9 — track CNI plugin health and policies."""
from __future__ import annotations
def fleet_container_network_v9(plugins: list[dict]) -> dict:
    healthy_p = [p for p in plugins if p.get("healthy")]
    pods_networked = sum(p.get("pods", 0) for p in plugins)
    policies = sum(p.get("network_policies", 0) for p in plugins)
    return {"plugins": len(plugins), "healthy": len(healthy_p), "pods_networked": pods_networked,
            "network_policies": policies, "all_healthy": len(healthy_p) == len(plugins)}
