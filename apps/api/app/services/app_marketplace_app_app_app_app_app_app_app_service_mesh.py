"""Service mesh topology — map service dependencies and health."""
from __future__ import annotations


def build_mesh(services: list[dict], connections: list[dict]) -> dict:
    nodes = {}
    for s in services:
        sid = s["id"]
        nodes[sid] = {"id": sid, "name": s.get("name", sid), "status": s.get("status", "healthy"),
                      "latency_ms": s.get("latency_ms", 0), "rps": s.get("rps", 0),
                      "upstream": [], "downstream": []}
    for c in connections:
        src, dst = c["from"], c["to"]
        if src in nodes:
            nodes[src]["downstream"].append(dst)
        if dst in nodes:
            nodes[dst]["upstream"].append(src)
    unhealthy = [n for n in nodes.values() if n["status"] != "healthy"]
    critical_path = _find_critical(nodes)
    return {"nodes": list(nodes.values()), "total_services": len(nodes),
            "total_connections": len(connections),
            "unhealthy_count": len(unhealthy),
            "mesh_health": "degraded" if unhealthy else "healthy",
            "critical_path": critical_path}


def _find_critical(nodes: dict) -> list[str]:
    """Find the service with most downstream deps (highest blast radius)."""
    ranked = sorted(nodes.values(), key=lambda n: len(n["downstream"]), reverse=True)
    return [n["id"] for n in ranked[:3] if n["downstream"]]
