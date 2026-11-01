"""Fleet AKS — track Azure Kubernetes Service health."""
from __future__ import annotations
def fleet_aks_status(clusters: list[dict]) -> dict:
    running = [c for c in clusters if c.get("power_state") == "Running"]
    total_nodes = sum(c.get("nodes", 0) for c in clusters)
    upgrades_available = [c for c in clusters if c.get("upgrade_available", False)]
    return {"clusters": len(clusters), "running": len(running), "nodes": total_nodes,
            "upgrades_available": len(upgrades_available), "all_running": len(running) == len(clusters)}
