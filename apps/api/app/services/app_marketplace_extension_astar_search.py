"""A* Search — optimal pathfinding with heuristic for weighted graphs.

Implements:
- A* algorithm: f(n) = g(n) + h(n)
- Configurable heuristic function
- Path reconstruction
- Visited node tracking for visualization
- Comparison: A* vs Dijkstra (A* with h=0)
- Multi-goal search (find closest of several targets)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import heapq
import math


@dataclass
class SearchResult:
    path: list[str]
    cost: float
    nodes_explored: int
    algorithm: str


class AStarSearchService:
    def __init__(self):
        self._nodes: dict[str, tuple[float, float]] = {}  # node → (x, y) for heuristic
        self._edges: dict[str, list[tuple[str, float]]] = {}  # node → [(neighbor, weight)]

    def add_node(self, node_id: str, x: float = 0, y: float = 0) -> None:
        self._nodes[node_id] = (x, y)
        if node_id not in self._edges:
            self._edges[node_id] = []

    def add_edge(self, from_node: str, to_node: str, weight: float = 1.0,
                 bidirectional: bool = True) -> None:
        if from_node not in self._edges:
            self._edges[from_node] = []
        self._edges[from_node].append((to_node, weight))
        if bidirectional:
            if to_node not in self._edges:
                self._edges[to_node] = []
            self._edges[to_node].append((from_node, weight))

    def _euclidean(self, a: str, b: str) -> float:
        if a not in self._nodes or b not in self._nodes:
            return 0
        ax, ay = self._nodes[a]
        bx, by = self._nodes[b]
        return math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)

    def _manhattan(self, a: str, b: str) -> float:
        if a not in self._nodes or b not in self._nodes:
            return 0
        ax, ay = self._nodes[a]
        bx, by = self._nodes[b]
        return abs(ax - bx) + abs(ay - by)

    def search(self, start: str, goal: str,
               heuristic: str = "euclidean") -> SearchResult:
        """A* search from start to goal."""
        h_fn = self._euclidean if heuristic == "euclidean" else self._manhattan

        open_set: list[tuple[float, str]] = [(0, start)]
        g_score: dict[str, float] = {start: 0}
        came_from: dict[str, str] = {}
        explored = 0

        while open_set:
            _, current = heapq.heappop(open_set)
            explored += 1

            if current == goal:
                path = self._reconstruct(came_from, current)
                return SearchResult(path, g_score[current], explored, "astar")

            for neighbor, weight in self._edges.get(current, []):
                tentative = g_score[current] + weight
                if tentative < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    f = tentative + h_fn(neighbor, goal)
                    heapq.heappush(open_set, (f, neighbor))

        return SearchResult([], float('inf'), explored, "astar")

    def dijkstra(self, start: str, goal: str) -> SearchResult:
        """Dijkstra = A* with h(n) = 0."""
        open_set: list[tuple[float, str]] = [(0, start)]
        g_score: dict[str, float] = {start: 0}
        came_from: dict[str, str] = {}
        explored = 0

        while open_set:
            cost, current = heapq.heappop(open_set)
            if cost > g_score.get(current, float('inf')):
                continue
            explored += 1
            if current == goal:
                return SearchResult(self._reconstruct(came_from, current),
                                    g_score[current], explored, "dijkstra")
            for neighbor, weight in self._edges.get(current, []):
                tentative = g_score[current] + weight
                if tentative < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    heapq.heappush(open_set, (tentative, neighbor))

        return SearchResult([], float('inf'), explored, "dijkstra")

    def find_nearest(self, start: str, goals: list[str]) -> SearchResult:
        """Find the nearest goal from a set of targets."""
        best: SearchResult | None = None
        for goal in goals:
            result = self.search(start, goal)
            if result.path and (not best or result.cost < best.cost):
                best = result
        return best or SearchResult([], float('inf'), 0, "astar")

    def _reconstruct(self, came_from: dict, current: str) -> list[str]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
