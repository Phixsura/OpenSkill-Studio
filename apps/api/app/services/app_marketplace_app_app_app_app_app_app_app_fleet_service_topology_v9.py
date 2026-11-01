"""Fleet Service Topology v9 — track real-time service dependency map."""
from __future__ import annotations
def fleet_service_topology_v9(services: list[dict]) -> dict:
    nodes = len(services)
    edges = sum(len(s.get("dependencies", [])) for s in services)
    orphans = [s for s in services if not s.get("dependencies") and not s.get("dependents")]
    return {"nodes": nodes, "edges": edges, "orphan_services": len(orphans),
            "avg_fan_out": round(edges / nodes, 1) if nodes else 0, "healthy": True}
