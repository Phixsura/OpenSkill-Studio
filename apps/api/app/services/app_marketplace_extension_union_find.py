"""Union-Find (Disjoint Set) — near O(1) union and find operations.

The classic data structure for connected components, Kruskal's MST,
and equivalence class problems.

Implements:
- Find with path compression (amortized O(α(n)) ≈ O(1))
- Union by rank (keeps tree balanced)
- Connected component queries
- Component size tracking
- Count of distinct components
"""
from __future__ import annotations


class UnionFindService:
    def __init__(self):
        self._parent: dict[str, str] = {}
        self._rank: dict[str, int] = {}
        self._size: dict[str, int] = {}
        self._count = 0

    def make_set(self, x: str) -> None:
        """Create a new singleton set."""
        if x in self._parent:
            return
        self._parent[x] = x
        self._rank[x] = 0
        self._size[x] = 1
        self._count += 1

    def find(self, x: str) -> str:
        """Find root with path compression."""
        if x not in self._parent:
            self.make_set(x)
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])  # path compression
        return self._parent[x]

    def union(self, x: str, y: str) -> bool:
        """Merge sets containing x and y. Returns False if already same set."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False  # already in same set

        # Union by rank
        if self._rank[rx] < self._rank[ry]:
            rx, ry = ry, rx  # ensure rx has higher rank
        self._parent[ry] = rx
        self._size[rx] += self._size[ry]
        if self._rank[rx] == self._rank[ry]:
            self._rank[rx] += 1
        self._count -= 1
        return True

    def connected(self, x: str, y: str) -> bool:
        """Check if x and y are in the same set."""
        return self.find(x) == self.find(y)

    def component_size(self, x: str) -> int:
        """Size of the component containing x."""
        return self._size[self.find(x)]

    @property
    def num_components(self) -> int:
        return self._count

    def get_components(self) -> dict[str, list[str]]:
        """Get all components as {root: [members]}."""
        components: dict[str, list[str]] = {}
        for x in self._parent:
            root = self.find(x)
            if root not in components:
                components[root] = []
            components[root].append(x)
        return components

    def largest_component(self) -> list[str]:
        """Return the largest connected component."""
        components = self.get_components()
        if not components:
            return []
        return max(components.values(), key=len)
