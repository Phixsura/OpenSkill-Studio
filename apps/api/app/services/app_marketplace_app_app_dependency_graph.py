"""Dependency graph — package dependency tree analysis."""

import html


def build_dependency_graph(*, packages: list[dict]) -> dict:
    nodes = {}
    edges = []
    for pkg in packages:
        name = pkg["name"]
        nodes[name] = {
            "name": html.escape(name),
            "version": pkg.get("version", "latest"),
            "size_kb": pkg.get("size_kb", 0),
            "dep_count": len(pkg.get("dependencies", [])),
        }
        for dep in pkg.get("dependencies", []):
            edges.append({"from": name, "to": dep})

    total_size = sum(n["size_kb"] for n in nodes.values())
    leaf_nodes = [n for n in nodes if n not in {e["from"] for e in edges}]
    root_nodes = [n for n in nodes if n not in {e["to"] for e in edges}]
    return {"nodes": list(nodes.values()), "edges": edges,
            "total_packages": len(nodes), "total_size_kb": total_size,
            "leaf_count": len(leaf_nodes), "root_count": len(root_nodes),
            "max_depth": _calc_depth(nodes, edges)}


def _calc_depth(nodes: dict, edges: list[dict]) -> int:
    children: dict[str, list[str]] = {}
    for e in edges:
        children.setdefault(e["from"], []).append(e["to"])
    roots = [n for n in nodes if n not in {e["to"] for e in edges}]
    if not roots:
        return 0
    max_d = 0
    stack = [(r, 1) for r in roots]
    visited: set[str] = set()
    while stack:
        node, depth = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        max_d = max(max_d, depth)
        for c in children.get(node, []):
            stack.append((c, depth + 1))
    return max_d
