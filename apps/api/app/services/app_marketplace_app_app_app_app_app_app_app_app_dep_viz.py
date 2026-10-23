"""App dependency graph visualizer — map inter-app dependencies."""
from __future__ import annotations


def build_dep_graph(apps: list[dict]) -> dict:
    nodes = []
    edges = []
    for app in apps:
        nodes.append({"id": app["id"], "name": app.get("name", app["id"]),
                       "icon": app.get("icon", "📱")})
        for dep in app.get("depends_on", []):
            edges.append({"from": app["id"], "to": dep})
    # Find root nodes (no incoming edges)
    targets = {e["to"] for e in edges}
    roots = [n["id"] for n in nodes if n["id"] not in targets]
    # Find leaf nodes (no outgoing edges)
    sources = {e["from"] for e in edges}
    leaves = [n["id"] for n in nodes if n["id"] not in sources]
    return {"nodes": nodes, "edges": edges,
            "node_count": len(nodes), "edge_count": len(edges),
            "roots": roots, "leaves": leaves}
