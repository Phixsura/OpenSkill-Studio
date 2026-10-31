"""Service topology health — overlay health onto service topology."""
from __future__ import annotations


def topology_health_summary(nodes: list[dict], edges: list[dict]) -> dict:
    healthy_nodes = sum(1 for n in nodes if n.get("health") == "healthy")
    healthy_edges = sum(1 for e in edges if e.get("health") == "healthy")
    critical_path = [e for e in edges if e.get("on_critical_path") and e.get("health") != "healthy"]
    overall = "healthy" if not critical_path and healthy_nodes == len(nodes) else (
        "critical" if critical_path else "degraded")
    return {"overall": overall, "nodes": len(nodes), "healthy_nodes": healthy_nodes,
            "edges": len(edges), "healthy_edges": healthy_edges,
            "critical_path_issues": len(critical_path),
            "node_health_pct": round(healthy_nodes / max(len(nodes), 1) * 100, 1)}
