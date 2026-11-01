"""Fleet Dependency Graph v9 — track service dependency topology."""
from __future__ import annotations
def fleet_dependency_graph_v9(nodes: list[dict]) -> dict:
    edges = sum(len(n.get("depends_on", [])) for n in nodes)
    circular = [n for n in nodes if n.get("circular")]
    return {"nodes": len(nodes), "edges": edges, "circular_deps": len(circular),
            "avg_fan_out": round(edges / len(nodes), 1) if nodes else 0,
            "healthy": len(circular) == 0}
