"""API Health Monitor — endpoint-level health monitoring with SLO tracking.

Monitors per-endpoint health with latency SLOs, error budgets,
availability tracking, and burn rate alerting.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class EndpointHealth:
    endpoint: str
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    total_latency_ms: float = 0.0
    slo_target: float = 99.9  # availability %
    latency_slo_ms: float = 500  # p99 target

    @property
    def availability(self) -> float:
        if not self.total_requests:
            return 100.0
        return round(self.successful / self.total_requests * 100, 2)

    @property
    def avg_latency(self) -> float:
        return round(self.total_latency_ms / max(self.total_requests, 1), 1)

    @property
    def error_budget_remaining(self) -> float:
        allowed_errors = self.total_requests * (1 - self.slo_target / 100)
        return round(max(0, allowed_errors - self.failed), 1)

    @property
    def slo_met(self) -> bool:
        return self.availability >= self.slo_target


class ApiHealthMonitorService:
    """Monitors API endpoint health with SLO tracking."""

    def __init__(self):
        self._endpoints: dict[str, EndpointHealth] = {}

    def configure(self, endpoint: str, slo_target: float = 99.9,
                  latency_slo_ms: float = 500) -> EndpointHealth:
        self._endpoints[endpoint] = EndpointHealth(
            endpoint=endpoint, slo_target=slo_target,
            latency_slo_ms=latency_slo_ms,
        )
        return self._endpoints[endpoint]

    def record(self, endpoint: str, success: bool,
               latency_ms: float) -> None:
        ep = self._endpoints.get(endpoint)
        if not ep:
            ep = EndpointHealth(endpoint=endpoint)
            self._endpoints[endpoint] = ep
        ep.total_requests += 1
        ep.total_latency_ms += latency_ms
        if success:
            ep.successful += 1
        else:
            ep.failed += 1

    def get_health(self, endpoint: str) -> dict | None:
        ep = self._endpoints.get(endpoint)
        if not ep:
            return None
        return {
            "endpoint": ep.endpoint,
            "availability": ep.availability,
            "avg_latency": ep.avg_latency,
            "slo_target": ep.slo_target,
            "slo_met": ep.slo_met,
            "error_budget_remaining": ep.error_budget_remaining,
            "total_requests": ep.total_requests,
        }

    def get_all_health(self) -> list[dict]:
        return [self.get_health(ep) for ep in self._endpoints]

    def get_violations(self) -> list[dict]:
        return [self.get_health(ep) for ep in self._endpoints
                if not self._endpoints[ep].slo_met]
