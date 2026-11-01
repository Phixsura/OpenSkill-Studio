"""Dependency tree analyzer — analyze service dependency trees."""
from __future__ import annotations
from collections import defaultdict


def build_tree(dependencies: list[dict]) -> dict:
    children: dict[str, list[str]] = defaultdict(list)
    all_nodes = set()
    child_nodes = set()
    for dep in dependencies:
        parent = dep["parent"]
        child = dep["child"]
        all_nodes.add(parent)
        all_nodes.add(child)
        child_nodes.add(child)
        children[parent].append(child)
    roots = sorted(all_nodes - child_nodes)
    def depth(node: str, visited: set | None = None) -> int:
        visited = visited or set()
        if node in visited:
            return 0
        visited.add(node)
        if node not in children:
            return 1
        return 1 + max((depth(c, visited) for c in children[node]), default=0)
    max_depth = max((depth(r) for r in roots), default=0)
    return {"roots": roots, "nodes": sorted(all_nodes), "edges": len(dependencies),
            "max_depth": max_depth, "tree": {k: sorted(v) for k, v in children.items()}}


def find_circular(dependencies: list[dict]) -> list[list[str]]:
    graph: dict[str, list[str]] = defaultdict(list)
    for d in dependencies:
        graph[d["parent"]].append(d["child"])
    cycles = []
    visited = set()
    path = []
    def dfs(node: str) -> None:
        if node in path:
            idx = path.index(node)
            cycles.append(path[idx:] + [node])
            return
        if node in visited:
            return
        path.append(node)
        for child in graph.get(node, []):
            dfs(child)
        path.pop()
        visited.add(node)
    for node in graph:
        dfs(node)
    return cycles
