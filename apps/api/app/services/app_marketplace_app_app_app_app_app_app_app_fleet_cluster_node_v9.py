"""Fleet Cluster Node v9 — track individual node health and capacity."""
from __future__ import annotations
def fleet_cluster_node_v9(nodes: list[dict]) -> dict:
    ready = [n for n in nodes if n.get("status") == "Ready"]
    not_ready = [n for n in nodes if n.get("status") != "Ready"]
    cpu_total = sum(n.get("cpu_cores", 0) for n in nodes)
    mem_total = sum(n.get("mem_gb", 0) for n in nodes)
    return {"nodes": len(nodes), "ready": len(ready), "not_ready": len(not_ready),
            "cpu_cores": cpu_total, "mem_gb": round(mem_total, 1), "healthy": len(not_ready) == 0}
