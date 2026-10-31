"""App API Developer API Health Check Scheduler — scheduled endpoint health checks."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class HealthCheck:
    check_id: str
    endpoint: str
    interval_seconds: int
    expected_status: int = 200
    timeout_ms: int = 5000
    enabled: bool = True
    last_result: str = "unknown"  # "healthy", "unhealthy", "timeout", "unknown"
    last_checked_at: float = 0.0
    consecutive_failures: int = 0

class AppAPIDeveloperAPIApiHealthCheckScheduler:
    def __init__(self) -> None:
        self._checks: dict[tuple[str, str], HealthCheck] = {}

    def schedule(self, installation_id: str, check_id: str, endpoint: str, interval_seconds: int, expected_status: int = 200, timeout_ms: int = 5000) -> HealthCheck:
        if not installation_id: raise ValueError("installation_id is required")
        if interval_seconds < 10: raise ValueError("interval must be at least 10 seconds")
        key = (installation_id, check_id)
        if key in self._checks: raise ValueError(f"Check {check_id} exists")
        c = HealthCheck(check_id=check_id, endpoint=endpoint, interval_seconds=interval_seconds, expected_status=expected_status, timeout_ms=timeout_ms)
        self._checks[key] = c
        return c

    def record_result(self, installation_id: str, check_id: str, status_code: int, response_time_ms: float) -> HealthCheck:
        c = self._get(installation_id, check_id)
        c.last_checked_at = time.time()
        if response_time_ms > c.timeout_ms:
            c.last_result = "timeout"
            c.consecutive_failures += 1
        elif status_code == c.expected_status:
            c.last_result = "healthy"
            c.consecutive_failures = 0
        else:
            c.last_result = "unhealthy"
            c.consecutive_failures += 1
        return c

    def unhealthy_checks(self, installation_id: str) -> list[HealthCheck]:
        return [c for (inst, _), c in self._checks.items() if inst == installation_id and c.last_result in ("unhealthy", "timeout")]

    def all_checks(self, installation_id: str) -> list[HealthCheck]:
        return [c for (inst, _), c in self._checks.items() if inst == installation_id]

    def _get(self, installation_id: str, check_id: str) -> HealthCheck:
        key = (installation_id, check_id)
        c = self._checks.get(key)
        if c is None: raise KeyError(f"Check {check_id} not found")
        return c
