"""Service graph explorer — navigate the complete service architecture."""
from __future__ import annotations


def build_service_graph(services: list[dict]) -> dict:
    nodes = []
    edges = []
    for s in services:
        nodes.append({"id": s["name"], "type": s.get("type", "service"),
                       "team": s.get("team", ""), "healthy": s.get("healthy", True)})
        for dep in s.get("depends_on", []):
            edges.append({"from": s["name"], "to": dep})
    healthy = sum(1 for n in nodes if n["healthy"])
    teams = sorted({n["team"] for n in nodes if n["team"]})
    return {"nodes": nodes, "edges": edges, "node_count": len(nodes),
            "edge_count": len(edges), "healthy": healthy,
            "teams": teams, "team_count": len(teams)}


def find_path(graph: dict, start: str, end: str) -> dict:
    adj: dict[str, list[str]] = {}
    for e in graph["edges"]:
        adj.setdefault(e["from"], []).append(e["to"])
    visited = set()
    queue = [[start]]
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node == end:
            return {"found": True, "path": path, "hops": len(path) - 1}
        if node not in visited:
            visited.add(node)
            for neighbor in adj.get(node, []):
                queue.append(path + [neighbor])
    return {"found": False, "path": [], "hops": -1}
