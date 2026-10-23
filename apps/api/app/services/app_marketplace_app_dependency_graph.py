"""App dependency graph — analyze and visualize app dependencies."""


def build_dependency_graph(*, app_id: str, app_name: str,
                            dependencies: list[dict]) -> dict:
    nodes = [{"id": app_id, "name": app_name, "type": "root"}]
    edges = []
    for dep in dependencies:
        nodes.append({"id": dep["id"], "name": dep["name"], "type": "dependency",
                       "version": dep.get("version", "latest")})
        edges.append({"from": app_id, "to": dep["id"], "kind": dep.get("kind", "required")})
        for sub in dep.get("sub_deps", []):
            nodes.append({"id": sub["id"], "name": sub["name"], "type": "transitive"})
            edges.append({"from": dep["id"], "to": sub["id"], "kind": "transitive"})
    unique_nodes = {n["id"]: n for n in nodes}
    return {
        "app_id": app_id,
        "nodes": list(unique_nodes.values()),
        "edges": edges,
        "total_dependencies": len(unique_nodes) - 1,
        "has_circular": False,
        "depth": max((1 for d in dependencies if d.get("sub_deps")), default=0) + 1 if dependencies else 0,
    }
