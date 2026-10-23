"""Dependency graph — track and analyze app dependencies."""
from __future__ import annotations


def build_dep_graph(deps: list[dict]) -> dict:
    nodes = {}
    edges = []
    for d in deps:
        src = d["from"]
        tgt = d["to"]
        nodes.setdefault(src, {"id": src, "in": 0, "out": 0})
        nodes.setdefault(tgt, {"id": tgt, "in": 0, "out": 0})
        nodes[src]["out"] += 1
        nodes[tgt]["in"] += 1
        edges.append({"source": src, "target": tgt, "type": d.get("type", "runtime")})
    roots = [n for n in nodes.values() if n["in"] == 0]
    leaves = [n for n in nodes.values() if n["out"] == 0]
    return {"nodes": list(nodes.values()), "edges": edges,
            "node_count": len(nodes), "edge_count": len(edges),
            "roots": [r["id"] for r in roots],
            "leaves": [l["id"] for l in leaves]}


def find_circular(deps: list[dict]) -> list[list[str]]:
    adj: dict[str, list[str]] = {}
    for d in deps:
        adj.setdefault(d["from"], []).append(d["to"])
    visited, stack, cycles = set(), set(), []
    def dfs(node: str, path: list[str]) -> None:
        if node in stack:
            idx = path.index(node)
            cycles.append(path[idx:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        stack.add(node)
        for nb in adj.get(node, []):
            dfs(nb, path + [node])
        stack.discard(node)
    for n in adj:
        dfs(n, [])
    return cycles
