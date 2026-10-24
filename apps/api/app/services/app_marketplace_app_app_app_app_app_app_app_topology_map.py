"""Service topology mapper — visualize service relationships."""
from __future__ import annotations


def build_topology(services: list[dict]) -> dict:
    nodes = []
    edges = []
    layers: dict[str, list[str]] = {}
    for s in services:
        layer = s.get("layer", "application")
        nodes.append({"name": s["name"], "layer": layer, "healthy": s.get("healthy", True)})
        layers.setdefault(layer, []).append(s["name"])
        for dep in s.get("depends_on", []):
            edges.append({"from": s["name"], "to": dep, "protocol": s.get("protocol", "http")})
    healthy = sum(1 for n in nodes if n["healthy"])
    return {"nodes": nodes, "edges": edges, "layers": layers,
            "node_count": len(nodes), "edge_count": len(edges),
            "healthy": healthy, "layer_count": len(layers)}


def find_critical_path(topology: dict) -> list[str]:
    incoming = {}
    for e in topology["edges"]:
        incoming.setdefault(e["to"], []).append(e["from"])
    most_dependents = max(incoming.items(), key=lambda x: len(x[1])) if incoming else (None, [])
    return [most_dependents[0]] if most_dependents[0] else []
