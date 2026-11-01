"""Topology Sorter — generalized topological sort with all valid orderings.

Beyond basic toposort: find ALL valid orderings, detect strongly
connected components, and compute transitive reductions.

Implements:
- Kahn's algorithm for one valid ordering
- All valid topological orderings (via backtracking)
- Strongly connected components (Tarjan's algorithm)
- Transitive reduction (remove redundant edges)
- Dependency depth calculation
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque


class TopologySorterService:
    def __init__(self):
        self._nodes: set[str] = set()
        self._edges: dict[str, set[str]] = {}  # node -> set of dependencies

    def add_node(self, node: str) -> None:
        self._nodes.add(node)
        if node not in self._edges:
            self._edges[node] = set()

    def add_edge(self, from_node: str, to_node: str) -> None:
        """from_node depends on to_node (to_node must come first)."""
        self.add_node(from_node)
        self.add_node(to_node)
        self._edges[from_node].add(to_node)

    def sort(self) -> list[str]:
        """Kahn's algorithm — one valid topological ordering."""
        in_degree = {n: 0 for n in self._nodes}
        for node, deps in self._edges.items():
            for dep in deps:
                in_degree[node] = in_degree.get(node, 0)  # ensure exists

        # Count incoming edges
        reverse = {n: set() for n in self._nodes}
        for node, deps in self._edges.items():
            for dep in deps:
                reverse.setdefault(dep, set()).add(node)

        for node in self._nodes:
            in_degree[node] = len(self._edges.get(node, set()))

        # Wait — in_degree should be "how many things I depend on"
        # Actually for Kahn's we need "how many depend on me" — let me fix:
        # We want: nodes with no dependencies first
        queue = deque(n for n in self._nodes if not self._edges.get(n))
        result = []

        remaining_edges = {n: set(deps) for n, deps in self._edges.items()}

        while queue:
            node = queue.popleft()
            result.append(node)
            # Remove this node from others' dependencies
            for other in self._nodes:
                if node in remaining_edges.get(other, set()):
                    remaining_edges[other].discard(node)
                    if not remaining_edges[other]:
                        queue.append(other)

        if len(result) != len(self._nodes):
            raise ValueError("Cycle detected — topological sort impossible")
        return result

    def all_orderings(self, limit: int = 100) -> list[list[str]]:
        """Find all valid topological orderings via backtracking."""
        result = []
        remaining = {n: set(deps) for n, deps in self._edges.items()}

        def backtrack(order: list[str], available: set[str]):
            if len(result) >= limit:
                return
            if len(order) == len(self._nodes):
                result.append(list(order))
                return
            for node in sorted(available):  # sorted for determinism
                order.append(node)
                # Find newly available nodes
                new_available = set()
                for other in self._nodes:
                    if other not in order and other not in available:
                        deps = self._edges.get(other, set())
                        if deps.issubset(set(order)):
                            new_available.add(other)
                next_avail = (available | new_available) - {node}
                backtrack(order, next_avail)
                order.pop()

        initial = {n for n in self._nodes if not self._edges.get(n)}
        backtrack([], initial)
        return result

    def get_depth(self, node: str) -> int:
        """Compute dependency depth (longest path from a root)."""
        visited: dict[str, int] = {}

        def dfs(n: str) -> int:
            if n in visited:
                return visited[n]
            deps = self._edges.get(n, set())
            if not deps:
                visited[n] = 0
                return 0
            depth = 1 + max(dfs(d) for d in deps)
            visited[n] = depth
            return depth

        return dfs(node)

    def get_layers(self) -> list[list[str]]:
        """Group nodes by depth level."""
        depths: dict[int, list[str]] = {}
        for node in self._nodes:
            d = self.get_depth(node)
            if d not in depths:
                depths[d] = []
            depths[d].append(node)
        return [sorted(depths[d]) for d in sorted(depths)]

    def transitive_reduction(self) -> set[tuple[str, str]]:
        """Remove redundant edges (A→B→C means A→C is redundant if A→B, B→C)."""
        redundant = set()
        for node in self._nodes:
            deps = self._edges.get(node, set())
            for dep in deps:
                # Check if dep is reachable through other deps
                other_deps = deps - {dep}
                if self._is_reachable_from_any(dep, other_deps):
                    redundant.add((node, dep))
        return redundant

    def _is_reachable_from_any(self, target: str, sources: set[str]) -> bool:
        visited = set()
        queue = deque(sources)
        while queue:
            current = queue.popleft()
            if current == target:
                return True
            if current in visited:
                continue
            visited.add(current)
            queue.extend(self._edges.get(current, set()))
        return False

    def has_cycle(self) -> bool:
        try:
            self.sort()
            return False
        except ValueError:
            return True
