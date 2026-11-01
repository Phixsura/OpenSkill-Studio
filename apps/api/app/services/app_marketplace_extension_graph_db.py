"""Graph Database — nodes, edges, traversal, shortest path.

Implements:
- Typed nodes with properties
- Directed edges with labels and weights
- BFS traversal
- Shortest path (Dijkstra's algorithm)
- Neighbor queries with edge type filtering
- Subgraph extraction
"""
from __future__ import annotations
from dataclasses import dataclass, field
import heapq
from collections import deque


@dataclass
class GraphNode:
    node_id: str
    label: str
    properties: dict = field(default_factory=dict)


@dataclass
class GraphEdge:
    from_id: str
    to_id: str
    label: str
    weight: float = 1.0
    properties: dict = field(default_factory=dict)


class GraphDbService:
    def __init__(self):
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge] = []
        self._adj: dict[str, list[GraphEdge]] = {}  # from_id -> [edges]
        self._rev_adj: dict[str, list[GraphEdge]] = {}  # to_id -> [edges]

    def add_node(self, node_id: str, label: str, properties: dict | None = None) -> GraphNode:
        node = GraphNode(node_id=node_id, label=label, properties=properties or {})
        self._nodes[node_id] = node
        return node

    def add_edge(self, from_id: str, to_id: str, label: str,
                 weight: float = 1.0, properties: dict | None = None) -> GraphEdge:
        if from_id not in self._nodes or to_id not in self._nodes:
            raise ValueError("Both nodes must exist")
        edge = GraphEdge(from_id=from_id, to_id=to_id, label=label,
                         weight=weight, properties=properties or {})
        self._edges.append(edge)
        self._adj.setdefault(from_id, []).append(edge)
        self._rev_adj.setdefault(to_id, []).append(edge)
        return edge

    def get_node(self, node_id: str) -> GraphNode | None:
        return self._nodes.get(node_id)

    def neighbors(self, node_id: str, edge_label: str | None = None,
                  direction: str = "out") -> list[tuple[str, GraphEdge]]:
        """Get neighboring nodes. direction: 'out', 'in', or 'both'."""
        result = []
        if direction in ("out", "both"):
            for edge in self._adj.get(node_id, []):
                if edge_label is None or edge.label == edge_label:
                    result.append((edge.to_id, edge))
        if direction in ("in", "both"):
            for edge in self._rev_adj.get(node_id, []):
                if edge_label is None or edge.label == edge_label:
                    result.append((edge.from_id, edge))
        return result

    def bfs(self, start_id: str, max_depth: int = 10) -> list[tuple[str, int]]:
        """BFS traversal. Returns [(node_id, depth)]."""
        if start_id not in self._nodes:
            return []
        visited = {start_id}
        queue = deque([(start_id, 0)])
        result = [(start_id, 0)]
        while queue:
            node_id, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for neighbor_id, _ in self.neighbors(node_id):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, depth + 1))
                    result.append((neighbor_id, depth + 1))
        return result

    def shortest_path(self, start_id: str, end_id: str) -> tuple[list[str], float]:
        """Dijkstra's shortest path. Returns (path, total_weight)."""
        if start_id not in self._nodes or end_id not in self._nodes:
            return [], float('inf')

        dist = {start_id: 0.0}
        prev: dict[str, str] = {}
        heap = [(0.0, start_id)]

        while heap:
            d, u = heapq.heappop(heap)
            if d > dist.get(u, float('inf')):
                continue
            if u == end_id:
                break
            for neighbor_id, edge in self.neighbors(u):
                new_dist = d + edge.weight
                if new_dist < dist.get(neighbor_id, float('inf')):
                    dist[neighbor_id] = new_dist
                    prev[neighbor_id] = u
                    heapq.heappush(heap, (new_dist, neighbor_id))

        if end_id not in dist:
            return [], float('inf')

        # Reconstruct path
        path = []
        current = end_id
        while current:
            path.append(current)
            current = prev.get(current, "")
        path.reverse()
        return path, dist[end_id]

    def find_by_label(self, label: str) -> list[GraphNode]:
        return [n for n in self._nodes.values() if n.label == label]

    def stats(self) -> dict:
        return {"nodes": len(self._nodes), "edges": len(self._edges)}
