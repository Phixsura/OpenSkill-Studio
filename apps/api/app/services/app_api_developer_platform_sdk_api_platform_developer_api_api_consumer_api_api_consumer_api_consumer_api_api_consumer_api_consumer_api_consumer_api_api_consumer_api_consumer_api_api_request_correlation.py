"""Consumer API Request Correlation — correlate requests across services."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import secrets
import structlog

log = structlog.get_logger()

@dataclass
class CorrelatedRequest:
    correlation_id: str
    consumer_id: str
    method: str
    path: str
    status_code: int = 0
    latency_ms: float = 0.0
    parent_id: str | None = None
    timestamp: datetime | None = None
    service: str = ""

@dataclass
class CorrelationChain:
    root_id: str
    requests: list[CorrelatedRequest]
    total_latency_ms: float
    service_count: int

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiRequestCorrelation:
    def __init__(self) -> None:
        self._requests: dict[tuple[str, str], CorrelatedRequest] = {}  # (inst, corr_id)

    def generate_id(self) -> str:
        return secrets.token_hex(16)

    def record(self, installation_id: str, request: CorrelatedRequest) -> CorrelatedRequest:
        if not installation_id:
            raise ValueError("installation_id is required")
        request.timestamp = request.timestamp or datetime.utcnow()
        self._requests[(installation_id, request.correlation_id)] = request
        return request

    def get_chain(self, installation_id: str, root_id: str) -> CorrelationChain:
        # Find root and all children
        chain: list[CorrelatedRequest] = []
        root = self._requests.get((installation_id, root_id))
        if root:
            chain.append(root)
        # Find children
        for (inst, _), req in self._requests.items():
            if inst == installation_id and req.parent_id == root_id:
                chain.append(req)
        chain.sort(key=lambda r: r.timestamp or datetime.min)
        total_lat = sum(r.latency_ms for r in chain)
        services = len({r.service for r in chain if r.service})
        return CorrelationChain(root_id=root_id, requests=chain, total_latency_ms=round(total_lat, 1), service_count=services)

    def find_by_consumer(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[CorrelatedRequest]:
        reqs = [r for (inst, _), r in self._requests.items() if inst == installation_id and r.consumer_id == consumer_id and r.parent_id is None]
        return sorted(reqs, key=lambda r: r.timestamp or datetime.min, reverse=True)[:limit]
