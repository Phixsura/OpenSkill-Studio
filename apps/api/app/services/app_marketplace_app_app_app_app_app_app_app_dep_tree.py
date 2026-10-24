"""Dependency tree — build hierarchical dependency trees."""
from __future__ import annotations


def build_tree(root: str, deps: dict[str, list[str]], max_depth: int = 10) -> dict:
    def _build(node: str, depth: int, visited: set) -> dict:
        if depth >= max_depth or node in visited:
            return {"name": node, "children": [], "circular": node in visited}
        visited = visited | {node}
        children = [_build(c, depth + 1, visited) for c in deps.get(node, [])]
        return {"name": node, "children": children, "depth": depth, "circular": False}
    tree = _build(root, 0, set())
    total = _count_nodes(tree)
    max_d = _max_depth(tree)
    return {"tree": tree, "total_nodes": total, "max_depth": max_d, "root": root}


def _count_nodes(node: dict) -> int:
    return 1 + sum(_count_nodes(c) for c in node.get("children", []))


def _max_depth(node: dict) -> int:
    children = node.get("children", [])
    if not children:
        return 0
    return 1 + max(_max_depth(c) for c in children)
