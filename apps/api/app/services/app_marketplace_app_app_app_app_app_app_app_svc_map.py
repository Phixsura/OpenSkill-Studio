"""Service map generator — generate visual service topology maps."""
from __future__ import annotations
from collections import defaultdict


def generate_service_map(connections: list[dict]) -> dict:
    nodes = set()
    edges = []
    by_source: dict[str, int] = defaultdict(int)
    for conn in connections:
        src = conn["source"]
        dst = conn["destination"]
        nodes.add(src)
        nodes.add(dst)
        by_source[src] += conn.get("request_count", 1)
        edges.append({"source": src, "destination": dst,
                       "requests": conn.get("request_count", 1),
                       "avg_latency_ms": conn.get("avg_latency_ms", 0),
                       "error_rate": conn.get("error_rate", 0)})
    # Identify entry points (nodes that are never destinations)
    destinations = set(e["destination"] for e in edges)
    entry_points = sorted(nodes - destinations)
    # Identify leaf nodes (nodes that are never sources)
    sources = set(e["source"] for e in edges)
    leaf_nodes = sorted(nodes - sources)
    return {"nodes": sorted(nodes), "edges": edges,
            "node_count": len(nodes), "edge_count": len(edges),
            "entry_points": entry_points, "leaf_nodes": leaf_nodes}


def detect_hotspots(edges: list[dict], threshold_rps: int = 1000) -> list[dict]:
    return [e for e in edges if e.get("requests", 0) > threshold_rps or e.get("error_rate", 0) > 5]
