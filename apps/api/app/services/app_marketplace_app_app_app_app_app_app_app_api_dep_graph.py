"""API dependency graph — map API-level dependencies between services."""
from __future__ import annotations


def build_api_graph(api_calls: list[dict]) -> dict:
    nodes = set()
    edges: dict[str, dict] = {}
    for call in api_calls:
        src = call["caller"]
        dst = call["callee"]
        nodes.add(src)
        nodes.add(dst)
        key = f"{src}→{dst}"
        if key not in edges:
            edges[key] = {"source": src, "target": dst, "calls": 0, "avg_ms": 0, "total_ms": 0}
        edges[key]["calls"] += call.get("count", 1)
        edges[key]["total_ms"] += call.get("total_latency_ms", 0)
    for e in edges.values():
        e["avg_ms"] = round(e["total_ms"] / max(e["calls"], 1), 1)
    sorted_edges = sorted(edges.values(), key=lambda e: -e["calls"])
    return {"nodes": sorted(nodes), "edges": sorted_edges,
            "node_count": len(nodes), "edge_count": len(edges),
            "total_calls": sum(e["calls"] for e in edges.values())}
