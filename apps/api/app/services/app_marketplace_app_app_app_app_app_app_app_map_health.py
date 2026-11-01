"""Service map health overlay — overlay health on the service map."""
from __future__ import annotations


def overlay_health(services: list[dict], connections: list[dict]) -> dict:
    svc_health = {}
    for s in services:
        svc_health[s["name"]] = s.get("health", "unknown")
    edges = []
    for c in connections:
        src_health = svc_health.get(c["source"], "unknown")
        dst_health = svc_health.get(c["destination"], "unknown")
        edge_health = "healthy" if src_health == "healthy" and dst_health == "healthy" else "degraded"
        edges.append({"source": c["source"], "destination": c["destination"],
                       "edge_health": edge_health, "latency_ms": c.get("latency_ms", 0)})
    healthy_svcs = sum(1 for h in svc_health.values() if h == "healthy")
    healthy_edges = sum(1 for e in edges if e["edge_health"] == "healthy")
    return {"nodes": [{"name": s["name"], "health": svc_health[s["name"]]} for s in services],
            "edges": edges, "healthy_nodes": healthy_svcs, "total_nodes": len(services),
            "healthy_edges": healthy_edges, "total_edges": len(edges)}
