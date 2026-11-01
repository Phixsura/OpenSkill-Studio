"""Consumer API Endpoint Map — visual endpoint mapping with relationships."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class MapNode:
    node_id: str
    label: str
    node_type: str  # endpoint, service, database, cache, queue
    group: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class MapEdge:
    from_node: str
    to_node: str
    label: str = ""
    edge_type: str = "calls"  # calls, reads, writes, publishes, subscribes


@dataclass
class EndpointMap:
    """Visual mapping of endpoint relationships and dependencies."""

    _nodes: dict[str, MapNode] = field(default_factory=dict)
    _edges: list[MapEdge] = field(default_factory=list)

    def add_node(self, node: MapNode) -> dict:
        if node.node_id in self._nodes:
            raise ValueError(f"Node {node.node_id} already exists")
        self._nodes[node.node_id] = node
        return {"node_id": node.node_id, "type": node.node_type}

    def add_edge(self, edge: MapEdge) -> dict:
        if edge.from_node not in self._nodes or edge.to_node not in self._nodes:
            raise ValueError("Both nodes must exist")
        if edge.from_node == edge.to_node:
            raise ValueError("Self-edges not allowed")
        self._edges.append(edge)
        logger.info("edge_added", from_node=edge.from_node, to=edge.to_node)
        return {"from": edge.from_node, "to": edge.to_node, "type": edge.edge_type}

    def get_map(self) -> dict:
        groups: dict[str, list[dict]] = {}
        for n in self._nodes.values():
            g = n.group or "default"
            groups.setdefault(g, []).append({"id": n.node_id, "label": n.label, "type": n.node_type})
        edges = [{"from": e.from_node, "to": e.to_node, "label": e.label, "type": e.edge_type}
                 for e in self._edges]
        return {"groups": groups, "edges": edges,
                "node_count": len(self._nodes), "edge_count": len(self._edges)}

    def get_neighbors(self, node_id: str) -> dict:
        if node_id not in self._nodes:
            return {"error": "not_found"}
        outgoing = [{"to": e.to_node, "type": e.edge_type} for e in self._edges if e.from_node == node_id]
        incoming = [{"from": e.from_node, "type": e.edge_type} for e in self._edges if e.to_node == node_id]
        return {"node_id": node_id, "outgoing": outgoing, "incoming": incoming,
                "degree": len(outgoing) + len(incoming)}

    def find_path(self, start: str, end: str) -> list[str]:
        if start not in self._nodes or end not in self._nodes:
            return []
        adj: dict[str, list[str]] = {n: [] for n in self._nodes}
        for e in self._edges:
            adj[e.from_node].append(e.to_node)
        # BFS
        from collections import deque
        queue: deque[list[str]] = deque([[start]])
        visited = {start}
        while queue:
            path = queue.popleft()
            node = path[-1]
            if node == end:
                return path
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        return []

    def remove_node(self, node_id: str) -> dict:
        if node_id not in self._nodes:
            return {"removed": False}
        del self._nodes[node_id]
        self._edges = [e for e in self._edges if e.from_node != node_id and e.to_node != node_id]
        return {"removed": True}

    def get_stats(self) -> dict:
        by_type: dict[str, int] = {}
        for n in self._nodes.values():
            by_type[n.node_type] = by_type.get(n.node_type, 0) + 1
        return {
            "nodes": len(self._nodes), "edges": len(self._edges),
            "groups": len(set(n.group for n in self._nodes.values() if n.group)),
            "by_type": by_type,
        }
