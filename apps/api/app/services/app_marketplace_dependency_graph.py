"""Dependency graph — track inter-app dependencies and conflicts."""


def build_dependency_graph(*, apps: list[dict]) -> dict:
    nodes = []
    edges = []
    for app in apps:
        nodes.append({"id": app["id"], "name": app["name"]})
        for dep_id in app.get("depends_on", []):
            edges.append({"from": app["id"], "to": dep_id, "type": "depends_on"})
        for conflict_id in app.get("conflicts_with", []):
            edges.append({"from": app["id"], "to": conflict_id, "type": "conflicts"})
    return {"nodes": nodes, "edges": edges, "node_count": len(nodes), "edge_count": len(edges)}


def detect_circular_dependencies(*, edges: list[dict]) -> list[list[str]]:
    graph: dict[str, list[str]] = {}
    for e in edges:
        if e["type"] == "depends_on":
            graph.setdefault(e["from"], []).append(e["to"])
    cycles = []
    visited: set[str] = set()
    path: list[str] = []
    path_set: set[str] = set()

    def dfs(node: str) -> None:
        if node in path_set:
            idx = path.index(node)
            cycles.append(path[idx:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        path.append(node)
        path_set.add(node)
        for neighbor in graph.get(node, []):
            dfs(neighbor)
        path.pop()
        path_set.discard(node)

    for node in graph:
        dfs(node)
    return cycles


def check_conflicts(*, installed_apps: list[dict], new_app: dict) -> dict:
    new_conflicts = set(new_app.get("conflicts_with", []))
    conflicts = []
    for app in installed_apps:
        if app["id"] in new_conflicts or new_app["id"] in app.get("conflicts_with", []):
            conflicts.append({"app_id": app["id"], "app_name": app["name"]})
    return {"has_conflicts": len(conflicts) > 0, "conflicts": conflicts}
