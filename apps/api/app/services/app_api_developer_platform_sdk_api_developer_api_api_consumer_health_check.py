"""App API Developer Consumer Health Check — monitor consumer integration health."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerHealthCheck:
    consumer_id: str
    auth_healthy: bool = True
    api_calls_healthy: bool = True
    webhook_healthy: bool = True
    error_rate_pct: float = 0.0
    last_active_hours_ago: float = 0.0

    @property
    def overall_health(self) -> str:
        issues = sum(1 for h in [self.auth_healthy, self.api_calls_healthy, self.webhook_healthy] if not h)
        if issues >= 2 or self.error_rate_pct > 10: return "critical"
        if issues >= 1 or self.error_rate_pct > 5: return "degraded"
        if self.last_active_hours_ago > 72: return "inactive"
        return "healthy"

    @property
    def issue_count(self) -> int:
        return sum(1 for h in [self.auth_healthy, self.api_calls_healthy, self.webhook_healthy] if not h)

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerHealthCheck:
    def __init__(self) -> None:
        self._checks: dict[tuple[str, str], ConsumerHealthCheck] = {}

    def update(self, installation_id: str, consumer_id: str, **kwargs) -> ConsumerHealthCheck:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        c = ConsumerHealthCheck(consumer_id=consumer_id)
        for k, v in kwargs.items():
            if hasattr(c, k): setattr(c, k, v)
        self._checks[key] = c
        return c

    def unhealthy(self, installation_id: str) -> list[ConsumerHealthCheck]:
        return [c for (inst, _), c in self._checks.items() if inst == installation_id and c.overall_health != "healthy"]

    def critical(self, installation_id: str) -> list[ConsumerHealthCheck]:
        return [c for (inst, _), c in self._checks.items() if inst == installation_id and c.overall_health == "critical"]

    def all_checks(self, installation_id: str) -> list[ConsumerHealthCheck]:
        return [c for (inst, _), c in self._checks.items() if inst == installation_id]
