"""Consumer API Endpoint Dependency Graph — visualize endpoint call chains."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DependencyEdge:
    from_endpoint: str
    to_endpoint: str
    call_count: int = 0
    avg_latency_ms: float = 0.0
    error_rate_pct: float = 0.0

@dataclass
class EndpointNode:
    path: str
    method: str = "GET"
    incoming: int = 0
    outgoing: int = 0
    is_leaf: bool = False
    is_root: bool = False

@dataclass
class DependencyGraph:
    nodes: list[EndpointNode]
    edges: list[DependencyEdge]
    total_endpoints: int
    max_depth: int

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiEndpointDependencyGraph:
    def __init__(self) -> None:
        self._edges: dict[tuple[str, str, str], DependencyEdge] = {}  # (inst, from, to)

    def add_edge(self, installation_id: str, edge: DependencyEdge) -> DependencyEdge:
        if not installation_id:
            raise ValueError("installation_id is required")
        if edge.from_endpoint == edge.to_endpoint:
            raise ValueError("Self-loop not allowed")
        self._edges[(installation_id, edge.from_endpoint, edge.to_endpoint)] = edge
        return edge

    def record_call(self, installation_id: str, from_ep: str, to_ep: str, latency_ms: float, is_error: bool = False) -> DependencyEdge:
        key = (installation_id, from_ep, to_ep)
        edge = self._edges.get(key)
        if not edge:
            edge = DependencyEdge(from_endpoint=from_ep, to_endpoint=to_ep)
            self._edges[key] = edge
        n = edge.call_count + 1
        edge.avg_latency_ms = edge.avg_latency_ms + (latency_ms - edge.avg_latency_ms) / n
        edge.call_count = n
        if is_error:
            error_count = edge.error_rate_pct / 100 * (n - 1) + 1
            edge.error_rate_pct = round(error_count / n * 100, 2)
        return edge

    def build_graph(self, installation_id: str) -> DependencyGraph:
        edges = [e for (inst, _, _), e in self._edges.items() if inst == installation_id]
        all_eps: set[str] = set()
        out_count: dict[str, int] = {}
        in_count: dict[str, int] = {}
        for e in edges:
            all_eps.add(e.from_endpoint)
            all_eps.add(e.to_endpoint)
            out_count[e.from_endpoint] = out_count.get(e.from_endpoint, 0) + 1
            in_count[e.to_endpoint] = in_count.get(e.to_endpoint, 0) + 1
        nodes = []
        for ep in sorted(all_eps):
            inc = in_count.get(ep, 0)
            out = out_count.get(ep, 0)
            nodes.append(EndpointNode(path=ep, incoming=inc, outgoing=out, is_leaf=out == 0, is_root=inc == 0))
        # Simple max depth via BFS from roots
        max_depth = 0
        roots = [n.path for n in nodes if n.is_root]
        for root in roots:
            visited: set[str] = set()
            queue = [(root, 0)]
            while queue:
                ep, depth = queue.pop(0)
                if ep in visited:
                    continue
                visited.add(ep)
                max_depth = max(max_depth, depth)
                for e in edges:
                    if e.from_endpoint == ep:
                        queue.append((e.to_endpoint, depth + 1))
        return DependencyGraph(nodes=nodes, edges=edges, total_endpoints=len(all_eps), max_depth=max_depth)
