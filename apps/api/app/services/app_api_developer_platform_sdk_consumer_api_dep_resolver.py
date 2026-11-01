"""Endpoint Dependency Resolver — topological sort with cycle detection."""
from __future__ import annotations

import structlog
from collections import deque
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class DependencyResolver:
    """Resolve endpoint execution order via topological sort."""

    _deps: dict[str, set[str]] = field(default_factory=dict)

    def add_endpoint(self, endpoint_id: str) -> dict:
        if endpoint_id not in self._deps:
            self._deps[endpoint_id] = set()
        return {"endpoint_id": endpoint_id, "registered": True}

    def add_dependency(self, endpoint_id: str, depends_on: str) -> dict:
        if endpoint_id == depends_on:
            raise ValueError("Endpoint cannot depend on itself")
        self._deps.setdefault(endpoint_id, set()).add(depends_on)
        self._deps.setdefault(depends_on, set())
        logger.info("dependency_added", endpoint=endpoint_id, depends_on=depends_on)
        return {"endpoint_id": endpoint_id, "depends_on": depends_on}

    def remove_dependency(self, endpoint_id: str, depends_on: str) -> dict:
        deps = self._deps.get(endpoint_id, set())
        deps.discard(depends_on)
        return {"removed": True}

    def get_dependencies(self, endpoint_id: str) -> dict:
        direct = self._deps.get(endpoint_id, set())
        # Transitive closure via BFS
        visited: set[str] = set()
        queue = deque(direct)
        while queue:
            dep = queue.popleft()
            if dep in visited:
                continue
            visited.add(dep)
            queue.extend(self._deps.get(dep, set()) - visited)
        return {
            "endpoint_id": endpoint_id,
            "direct": sorted(direct),
            "transitive": sorted(visited),
        }

    def detect_cycles(self) -> list[list[str]]:
        """Detect cycles using DFS coloring."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {n: WHITE for n in self._deps}
        parent: dict[str, str | None] = {n: None for n in self._deps}
        cycles: list[list[str]] = []

        def dfs(node: str) -> None:
            color[node] = GRAY
            for neighbor in self._deps.get(node, set()):
                if color.get(neighbor, WHITE) == GRAY:
                    # Found cycle — reconstruct
                    cycle = [neighbor, node]
                    p = parent.get(node)
                    while p and p != neighbor:
                        cycle.append(p)
                        p = parent.get(p)
                    cycle.reverse()
                    cycles.append(cycle)
                elif color.get(neighbor, WHITE) == WHITE:
                    parent[neighbor] = node
                    dfs(neighbor)
            color[node] = BLACK

        for node in list(self._deps):
            if color.get(node, WHITE) == WHITE:
                dfs(node)
        return cycles

    def resolve_order(self) -> dict:
        """Kahn's algorithm for topological sort."""
        cycles = self.detect_cycles()
        if cycles:
            return {"success": False, "reason": "cycles_detected", "cycles": cycles}
        in_degree: dict[str, int] = {n: 0 for n in self._deps}
        for node, deps in self._deps.items():
            for dep in deps:
                in_degree.setdefault(node, 0)
                # dep must come before node, so node has in-degree from dep
        # Reverse: build adjacency as dep -> [node]
        adj: dict[str, list[str]] = {n: [] for n in self._deps}
        for node, deps in self._deps.items():
            for dep in deps:
                adj.setdefault(dep, []).append(node)
                in_degree[node] = in_degree.get(node, 0) + 1
        # Reset in_degree properly
        in_degree = {n: 0 for n in self._deps}
        for node, deps in self._deps.items():
            in_degree.setdefault(node, 0)
            for dep in deps:
                in_degree[node] += 1
        queue = deque(n for n, d in in_degree.items() if d == 0)
        order: list[str] = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return {"success": True, "order": order, "total": len(order)}

    def get_roots(self) -> list[str]:
        """Endpoints with no dependencies."""
        return sorted(e for e, deps in self._deps.items() if not deps)

    def get_leaves(self) -> list[str]:
        """Endpoints that nothing depends on."""
        depended_on: set[str] = set()
        for deps in self._deps.values():
            depended_on.update(deps)
        return sorted(e for e in self._deps if e not in depended_on)
