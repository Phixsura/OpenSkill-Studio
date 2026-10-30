"""API Consumer Webhook Health Check — verify webhook endpoint availability."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class HealthCheckResult:
    check_id: str
    endpoint: str
    healthy: bool
    status_code: int = 0
    latency_ms: float = 0.0
    error: str = ""
    checked_at: float = field(default_factory=time.time)

@dataclass
class EndpointHealth:
    endpoint: str
    consumer_id: str
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_healthy: float = 0.0
    total_checks: int = 0
    total_failures: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookHealthCheck:
    def __init__(self) -> None:
        self._health: dict[tuple[str, str, str], EndpointHealth] = {}

    def record_check(self, installation_id: str, consumer_id: str, endpoint: str, healthy: bool, status_code: int = 0, latency_ms: float = 0.0) -> EndpointHealth:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id, endpoint)
        h = self._health.get(key)
        if h is None:
            h = EndpointHealth(endpoint=endpoint, consumer_id=consumer_id)
            self._health[key] = h
        h.total_checks += 1
        if healthy:
            h.consecutive_successes += 1
            h.consecutive_failures = 0
            h.last_healthy = time.time()
        else:
            h.consecutive_failures += 1
            h.consecutive_successes = 0
            h.total_failures += 1
        return h

    def is_healthy(self, installation_id: str, consumer_id: str, endpoint: str) -> bool:
        h = self._health.get((installation_id, consumer_id, endpoint))
        if h is None: return True  # no data = assumed healthy
        return h.consecutive_failures < 3

    def unhealthy_endpoints(self, installation_id: str, failure_threshold: int = 3) -> list[EndpointHealth]:
        return [h for (inst, _, _), h in self._health.items()
                if inst == installation_id and h.consecutive_failures >= failure_threshold]

    def availability(self, installation_id: str, consumer_id: str, endpoint: str) -> float:
        h = self._health.get((installation_id, consumer_id, endpoint))
        if h is None or h.total_checks == 0: return 100.0
        return round(((h.total_checks - h.total_failures) / h.total_checks) * 100, 2)

    def list_health(self, installation_id: str) -> list[EndpointHealth]:
        return [h for (inst, _, _), h in self._health.items() if inst == installation_id]
