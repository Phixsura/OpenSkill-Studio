"""API Consumer Gateway Health — monitor API gateway health across regions."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class GatewayNode:
    node_id: str
    region: str
    healthy: bool = True
    requests_per_second: float = 0.0
    error_rate: float = 0.0
    latency_p99_ms: float = 0.0
    connections: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiGatewayHealth:
    def __init__(self) -> None:
        self._nodes: dict[tuple[str, str], GatewayNode] = {}

    def update_node(self, installation_id: str, node: GatewayNode) -> GatewayNode:
        if not installation_id: raise ValueError("installation_id is required")
        self._nodes[(installation_id, node.node_id)] = node
        return node

    def healthy_nodes(self, installation_id: str) -> list[GatewayNode]:
        return [n for (inst, _), n in self._nodes.items() if inst == installation_id and n.healthy]

    def unhealthy_nodes(self, installation_id: str) -> list[GatewayNode]:
        return [n for (inst, _), n in self._nodes.items() if inst == installation_id and not n.healthy]

    def by_region(self, installation_id: str) -> dict[str, list[GatewayNode]]:
        result: dict[str, list[GatewayNode]] = {}
        for (inst, _), n in self._nodes.items():
            if inst == installation_id: result.setdefault(n.region, []).append(n)
        return result

    def total_rps(self, installation_id: str) -> float:
        return round(sum(n.requests_per_second for (inst, _), n in self._nodes.items() if inst == installation_id), 1)

    def list_nodes(self, installation_id: str) -> list[GatewayNode]:
        return [n for (inst, _), n in self._nodes.items() if inst == installation_id]
