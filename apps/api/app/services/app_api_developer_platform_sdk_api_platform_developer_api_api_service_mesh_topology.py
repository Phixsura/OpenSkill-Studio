"""API Service Mesh Topology — visualize inter-service communication topology."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ServiceNode:
    service_id: str
    name: str
    version: str = ""
    healthy: bool = True
    request_rate: float = 0.0  # req/s

@dataclass
class ServiceEdge:
    source_id: str
    target_id: str
    protocol: str = "http"  # "http", "grpc", "tcp"
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    requests_per_sec: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiServiceMeshTopology:
    def __init__(self) -> None:
        self._nodes: dict[tuple[str, str], ServiceNode] = {}
        self._edges: dict[tuple[str, str, str], ServiceEdge] = {}

    def add_node(self, installation_id: str, node: ServiceNode) -> ServiceNode:
        if not installation_id: raise ValueError("installation_id is required")
        self._nodes[(installation_id, node.service_id)] = node
        return node

    def add_edge(self, installation_id: str, edge: ServiceEdge) -> ServiceEdge:
        if not installation_id: raise ValueError("installation_id is required")
        if (installation_id, edge.source_id) not in self._nodes: raise KeyError(f"Source {edge.source_id} not found")
        if (installation_id, edge.target_id) not in self._nodes: raise KeyError(f"Target {edge.target_id} not found")
        if edge.source_id == edge.target_id: raise ValueError("Self-loop not allowed")
        self._edges[(installation_id, edge.source_id, edge.target_id)] = edge
        return edge

    def get_dependencies(self, installation_id: str, service_id: str) -> list[ServiceEdge]:
        return [e for (inst, src, _), e in self._edges.items() if inst == installation_id and src == service_id]

    def get_dependents(self, installation_id: str, service_id: str) -> list[ServiceEdge]:
        return [e for (inst, _, tgt), e in self._edges.items() if inst == installation_id and tgt == service_id]

    def unhealthy_nodes(self, installation_id: str) -> list[ServiceNode]:
        return [n for (inst, _), n in self._nodes.items() if inst == installation_id and not n.healthy]

    def high_latency_edges(self, installation_id: str, threshold_ms: float = 200) -> list[ServiceEdge]:
        return [e for (inst, _, _), e in self._edges.items() if inst == installation_id and e.avg_latency_ms > threshold_ms]

    def list_nodes(self, installation_id: str) -> list[ServiceNode]:
        return [n for (inst, _), n in self._nodes.items() if inst == installation_id]
