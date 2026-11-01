"""Service startup order resolver — topological sort for service startup."""
from __future__ import annotations
from collections import defaultdict


def resolve_startup_order(dependencies: dict[str, list[str]]) -> dict:
    in_degree: dict[str, int] = defaultdict(int)
    all_services = set(dependencies.keys())
    for deps in dependencies.values():
        all_services.update(deps)
    for s in all_services:
        in_degree.setdefault(s, 0)
    for deps in dependencies.values():
        for d in deps:
            in_degree[d]  # ensure exists
    # Reverse: we need deps to start first
    graph: dict[str, list[str]] = defaultdict(list)
    for svc, deps in dependencies.items():
        for d in deps:
            graph[d].append(svc)
            in_degree[svc] += 1
    # Kahn's algorithm
    queue = [s for s in all_services if in_degree[s] == 0]
    order = []
    while queue:
        queue.sort()
        node = queue.pop(0)
        order.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    has_cycle = len(order) != len(all_services)
    phases = []
    if not has_cycle:
        phase_map: dict[str, int] = {}
        for s in order:
            deps = dependencies.get(s, [])
            phase = max((phase_map.get(d, 0) for d in deps), default=0) + 1 if deps else 1
            phase_map[s] = phase
        for p in sorted(set(phase_map.values())):
            phases.append(sorted(s for s, ph in phase_map.items() if ph == p))
    return {"order": order, "phases": phases, "has_cycle": has_cycle, "total": len(all_services)}
