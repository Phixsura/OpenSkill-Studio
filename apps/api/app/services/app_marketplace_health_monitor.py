"""Health Monitor — track extension health, uptime, and error rates.

Monitors extension runtime health with heartbeats, error tracking,
automatic status degradation, and incident reporting.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    extension_id: str
    status: HealthStatus
    response_time_ms: float
    checked_at: str
    error: str = ""


class HealthMonitor:
    """Monitors extension health with heartbeats and error tracking."""

    def __init__(self, degraded_threshold: float = 1000.0, unhealthy_threshold: float = 5000.0,
                 error_rate_threshold: float = 0.05):
        self._checks: dict[str, list[HealthCheck]] = {}
        self._error_counts: dict[str, int] = {}
        self._total_counts: dict[str, int] = {}
        self._degraded_ms = degraded_threshold
        self._unhealthy_ms = unhealthy_threshold
        self._error_threshold = error_rate_threshold
        self._incidents: list[dict] = []

    def record_heartbeat(self, extension_id: str, response_time_ms: float, error: str = "") -> HealthCheck:
        """Record a health check heartbeat."""
        self._total_counts[extension_id] = self._total_counts.get(extension_id, 0) + 1
        if error:
            self._error_counts[extension_id] = self._error_counts.get(extension_id, 0) + 1

        if error:
            status = HealthStatus.UNHEALTHY
        elif response_time_ms > self._unhealthy_ms:
            status = HealthStatus.UNHEALTHY
        elif response_time_ms > self._degraded_ms:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        check = HealthCheck(
            extension_id=extension_id, status=status,
            response_time_ms=response_time_ms, error=error,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )
        self._checks.setdefault(extension_id, []).append(check)

        # Auto-create incident on unhealthy
        if status == HealthStatus.UNHEALTHY:
            self._incidents.append({
                "extension_id": extension_id, "status": status.value,
                "error": error, "response_time_ms": response_time_ms,
                "detected_at": check.checked_at,
            })
        return check

    def get_status(self, extension_id: str) -> HealthStatus:
        """Get current health status based on last check."""
        checks = self._checks.get(extension_id, [])
        if not checks:
            return HealthStatus.UNKNOWN
        return checks[-1].status

    def get_error_rate(self, extension_id: str) -> float:
        """Get error rate for an extension."""
        total = self._total_counts.get(extension_id, 0)
        if total == 0:
            return 0.0
        errors = self._error_counts.get(extension_id, 0)
        return round(errors / total, 4)

    def get_avg_response_time(self, extension_id: str, last_n: int = 10) -> float:
        """Get average response time from recent checks."""
        checks = self._checks.get(extension_id, [])[-last_n:]
        if not checks:
            return 0.0
        return round(sum(c.response_time_ms for c in checks) / len(checks), 2)

    def get_summary(self, extension_id: str) -> dict:
        return {
            "extension_id": extension_id,
            "status": self.get_status(extension_id).value,
            "error_rate": self.get_error_rate(extension_id),
            "avg_response_ms": self.get_avg_response_time(extension_id),
            "total_checks": self._total_counts.get(extension_id, 0),
        }

    def get_incidents(self, extension_id: str | None = None) -> list[dict]:
        if extension_id:
            return [i for i in self._incidents if i["extension_id"] == extension_id]
        return list(self._incidents)

    def list_unhealthy(self) -> list[str]:
        """List all extensions currently unhealthy."""
        return [eid for eid in self._checks if self.get_status(eid) == HealthStatus.UNHEALTHY]
