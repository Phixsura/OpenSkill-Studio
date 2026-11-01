"""Endpoint Service Mesh — service-to-service routing with circuit breaker."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class ServiceNode:
    service_id: str
    name: str
    version: str = "1.0.0"
    healthy: bool = True
    request_count: int = 0
    error_count: int = 0


@dataclass
class ServiceLink:
    from_service: str
    to_service: str
    protocol: str = "http"  # http, grpc
    timeout_ms: int = 5000
    retry_count: int = 3
    circuit_open: bool = False
    failure_count: int = 0
    failure_threshold: int = 5


@dataclass
class ServiceMesh:
    """Manage service-to-service communication with routing and circuit breakers."""

    _nodes: dict[str, ServiceNode] = field(default_factory=dict)
    _links: dict[str, ServiceLink] = field(default_factory=dict)  # "from->to" -> link

    def register_service(self, node: ServiceNode) -> dict:
        if node.service_id in self._nodes:
            raise ValueError(f"Service {node.service_id} already registered")
        self._nodes[node.service_id] = node
        logger.info("service_registered", service_id=node.service_id)
        return {"service_id": node.service_id, "total": len(self._nodes)}

    def add_link(self, link: ServiceLink) -> dict:
        if link.from_service not in self._nodes or link.to_service not in self._nodes:
            raise ValueError("Both services must be registered")
        key = f"{link.from_service}->{link.to_service}"
        self._links[key] = link
        logger.info("link_added", from_svc=link.from_service, to_svc=link.to_service)
        return {"link": key, "protocol": link.protocol}

    def route_request(self, from_service: str, to_service: str) -> dict:
        key = f"{from_service}->{to_service}"
        link = self._links.get(key)
        if not link:
            return {"routed": False, "reason": "no_link"}
        target = self._nodes.get(to_service)
        if not target or not target.healthy:
            return {"routed": False, "reason": "target_unhealthy"}
        if link.circuit_open:
            return {"routed": False, "reason": "circuit_open"}
        target.request_count += 1
        return {"routed": True, "target": to_service, "protocol": link.protocol,
                "timeout_ms": link.timeout_ms}

    def record_failure(self, from_service: str, to_service: str) -> dict:
        key = f"{from_service}->{to_service}"
        link = self._links.get(key)
        if not link:
            return {"error": "no_link"}
        link.failure_count += 1
        target = self._nodes.get(to_service)
        if target:
            target.error_count += 1
        if link.failure_count >= link.failure_threshold:
            link.circuit_open = True
            logger.warning("circuit_opened", link=key)
        return {"failure_count": link.failure_count, "circuit_open": link.circuit_open}

    def reset_circuit(self, from_service: str, to_service: str) -> dict:
        key = f"{from_service}->{to_service}"
        link = self._links.get(key)
        if not link:
            return {"error": "no_link"}
        link.circuit_open = False
        link.failure_count = 0
        return {"link": key, "circuit_open": False}

    def get_topology(self) -> dict:
        nodes = [{"id": n.service_id, "name": n.name, "healthy": n.healthy,
                  "requests": n.request_count, "errors": n.error_count}
                 for n in self._nodes.values()]
        links = [{"from": l.from_service, "to": l.to_service,
                  "protocol": l.protocol, "circuit_open": l.circuit_open}
                 for l in self._links.values()]
        return {"nodes": nodes, "links": links}

    def get_service_deps(self, service_id: str) -> dict:
        upstream = [l.from_service for l in self._links.values() if l.to_service == service_id]
        downstream = [l.to_service for l in self._links.values() if l.from_service == service_id]
        return {"service_id": service_id, "upstream": upstream, "downstream": downstream}

    def get_stats(self) -> dict:
        open_circuits = sum(1 for l in self._links.values() if l.circuit_open)
        return {
            "total_services": len(self._nodes),
            "total_links": len(self._links),
            "healthy_services": sum(1 for n in self._nodes.values() if n.healthy),
            "open_circuits": open_circuits,
        }
