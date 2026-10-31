"""Fleet AI Dependency Graph — track AI service dependency visualization."""
from __future__ import annotations
def fleet_ai_dependency_graph(graphs: list[dict]) -> dict:
    active = [g for g in graphs if g.get("active", True)]
    services = sum(g.get("services", 0) for g in graphs)
    edges = sum(g.get("edges", 0) for g in graphs)
    circular = sum(g.get("circular", 0) for g in graphs)
    return {"graphs": len(graphs), "active": len(active), "services": services,
            "edges": edges, "circular": circular, "healthy": circular == 0}
