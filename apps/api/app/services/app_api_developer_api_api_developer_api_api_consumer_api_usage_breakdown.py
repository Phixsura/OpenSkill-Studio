"""App API Developer Consumer API Usage Breakdown — per-consumer endpoint usage details."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointUsage:
    endpoint: str
    method: str
    call_count: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0.0

@dataclass
class ConsumerBreakdown:
    consumer_id: str
    endpoints: list[EndpointUsage] = field(default_factory=list)

    @property
    def total_calls(self) -> int:
        return sum(e.call_count for e in self.endpoints)

    @property
    def total_errors(self) -> int:
        return sum(e.error_count for e in self.endpoints)

    @property
    def unique_endpoints(self) -> int:
        return len(self.endpoints)

class AppAPIDeveloperAPIApiDeveloperApiApiConsumerApiUsageBreakdown:
    def __init__(self) -> None:
        self._breakdowns: dict[tuple[str, str], ConsumerBreakdown] = {}

    def record(self, installation_id: str, consumer_id: str, endpoint: str, method: str, calls: int, errors: int = 0, avg_latency_ms: float = 0.0) -> ConsumerBreakdown:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key not in self._breakdowns:
            self._breakdowns[key] = ConsumerBreakdown(consumer_id=consumer_id)
        b = self._breakdowns[key]
        existing = next((e for e in b.endpoints if e.endpoint == endpoint and e.method == method), None)
        if existing:
            existing.call_count += calls
            existing.error_count += errors
        else:
            b.endpoints.append(EndpointUsage(endpoint=endpoint, method=method, call_count=calls, error_count=errors, avg_latency_ms=avg_latency_ms))
        return b

    def get(self, installation_id: str, consumer_id: str) -> ConsumerBreakdown | None:
        return self._breakdowns.get((installation_id, consumer_id))

    def top_consumers(self, installation_id: str, limit: int = 10) -> list[ConsumerBreakdown]:
        breakdowns = [b for (inst, _), b in self._breakdowns.items() if inst == installation_id]
        return sorted(breakdowns, key=lambda b: b.total_calls, reverse=True)[:limit]

    def heaviest_endpoint_users(self, installation_id: str, endpoint: str) -> list[tuple[str, int]]:
        result = []
        for (inst, _), b in self._breakdowns.items():
            if inst != installation_id: continue
            for e in b.endpoints:
                if e.endpoint == endpoint:
                    result.append((b.consumer_id, e.call_count))
        return sorted(result, key=lambda x: x[1], reverse=True)
