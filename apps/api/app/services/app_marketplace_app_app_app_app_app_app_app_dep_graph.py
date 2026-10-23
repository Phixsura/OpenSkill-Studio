"""Dependency graph resolver — topological sort and cycle detection."""
from __future__ import annotations


def build_graph(nodes: list[dict]) -> dict:
    adj: dict[str, list[str]] = {}
    for n in nodes:
        adj[n["id"]] = n.get("depends_on", [])
    return {"nodes": list(adj.keys()), "edges": adj, "node_count": len(adj),
            "edge_count": sum(len(v) for v in adj.values())}


def topological_sort(graph: dict) -> dict:
    adj = graph["edges"]
    visited: set[str] = set()
    temp: set[str] = set()
    order: list[str] = []
    has_cycle = False
    cycle_nodes: list[str] = []

    def visit(node: str) -> bool:
        nonlocal has_cycle
        if node in temp:
            has_cycle = True
            cycle_nodes.append(node)
            return False
        if node in visited:
            return True
        temp.add(node)
        for dep in adj.get(node, []):
            if not visit(dep):
                if has_cycle:
                    cycle_nodes.append(node)
                return False
        temp.remove(node)
        visited.add(node)
        order.append(node)
        return True

    for n in adj:
        if n not in visited:
            visit(n)
    return {"order": order if not has_cycle else [], "has_cycle": has_cycle,
            "cycle_nodes": list(set(cycle_nodes)) if has_cycle else [],
            "build_phases": _phases(order, adj) if not has_cycle else []}


def _phases(order: list[str], adj: dict[str, list[str]]) -> list[list[str]]:
    depth: dict[str, int] = {}
    for n in order:
        deps = adj.get(n, [])
        depth[n] = max((depth.get(d, 0) for d in deps), default=-1) + 1
    phases: dict[int, list[str]] = {}
    for n, d in depth.items():
        phases.setdefault(d, []).append(n)
    return [phases[i] for i in sorted(phases)]
