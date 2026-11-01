"""Infrastructure overview — top-level infrastructure summary."""
from __future__ import annotations


def build_infra_overview(data: dict) -> dict:
    compute = data.get("compute", {})
    storage = data.get("storage", {})
    network = data.get("network", {})
    total_cost = round(sum(d.get("cost", 0) for d in [compute, storage, network]), 2)
    nodes = compute.get("nodes", 0)
    cpu_total = compute.get("cpu_cores", 0)
    mem_total = compute.get("memory_gb", 0)
    storage_tb = storage.get("total_tb", 0)
    bandwidth_gbps = network.get("bandwidth_gbps", 0)
    health = "healthy" if all(d.get("healthy", True) for d in [compute, storage, network]) else "degraded"
    return {"total_cost": total_cost, "display_cost": f"${total_cost:,.0f}/mo",
            "compute": {"nodes": nodes, "cpu_cores": cpu_total, "memory_gb": mem_total},
            "storage": {"total_tb": storage_tb},
            "network": {"bandwidth_gbps": bandwidth_gbps},
            "health": health}
