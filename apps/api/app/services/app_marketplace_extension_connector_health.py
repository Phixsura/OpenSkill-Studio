"""Connector Health Check — monitor connector endpoint availability.

Performs periodic health checks on connector endpoints, tracks uptime,
calculates SLA compliance, and triggers alerts on degradation.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    check_id: str
    connector_id: str
    endpoint_url: str
    status: HealthStatus
    response_time_ms: float
    status_code: int = 0
    error: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ConnectorHealthConfig:
    connector_id: str
    endpoint_url: str
    check_interval_seconds: int = 60
    timeout_ms: int = 5000
    degraded_threshold_ms: float = 2000
    failure_threshold: int = 3  # consecutive failures → DOWN


class ConnectorHealthService:
    """Monitors connector endpoint health with SLA tracking."""

    def __init__(self):
        self._configs: dict[str, ConnectorHealthConfig] = {}
        self._checks: list[HealthCheck] = []
        self._consecutive_failures: dict[str, int] = defaultdict(int)
        self._current_status: dict[str, HealthStatus] = {}

    def configure(self, connector_id: str, endpoint_url: str,
                  check_interval: int = 60, timeout_ms: int = 5000,
                  degraded_threshold_ms: float = 2000) -> ConnectorHealthConfig:
        config = ConnectorHealthConfig(
            connector_id=connector_id, endpoint_url=endpoint_url,
            check_interval_seconds=max(30, check_interval),
            timeout_ms=timeout_ms, degraded_threshold_ms=degraded_threshold_ms,
        )
        self._configs[connector_id] = config
        self._current_status[connector_id] = HealthStatus.UNKNOWN
        return config

    def record_check(self, connector_id: str, response_time_ms: float,
                     status_code: int = 200, error: str = "") -> HealthCheck:
        config = self._configs.get(connector_id)
        if not config:
            raise ValueError("Connector not configured")

        if error or status_code >= 500:
            status = HealthStatus.DOWN
            self._consecutive_failures[connector_id] += 1
        elif response_time_ms > config.degraded_threshold_ms:
            status = HealthStatus.DEGRADED
            self._consecutive_failures[connector_id] = 0
        else:
            status = HealthStatus.HEALTHY
            self._consecutive_failures[connector_id] = 0

        # Override to DOWN if consecutive failures exceed threshold
        if self._consecutive_failures[connector_id] >= config.failure_threshold:
            status = HealthStatus.DOWN

        self._current_status[connector_id] = status

        check = HealthCheck(
            check_id=f"hc_{secrets.token_urlsafe(8)}",
            connector_id=connector_id, endpoint_url=config.endpoint_url,
            status=status, response_time_ms=response_time_ms,
            status_code=status_code, error=error,
        )
        self._checks.append(check)
        return check

    def get_status(self, connector_id: str) -> HealthStatus:
        return self._current_status.get(connector_id, HealthStatus.UNKNOWN)

    def get_uptime(self, connector_id: str) -> dict:
        checks = [c for c in self._checks if c.connector_id == connector_id]
        if not checks:
            return {"uptime_percent": 0, "total_checks": 0}
        healthy = sum(1 for c in checks if c.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED))
        return {
            "uptime_percent": round(healthy / len(checks) * 100, 2),
            "total_checks": len(checks),
            "healthy": healthy,
            "degraded": sum(1 for c in checks if c.status == HealthStatus.DEGRADED),
            "down": sum(1 for c in checks if c.status == HealthStatus.DOWN),
        }

    def get_avg_response_time(self, connector_id: str) -> float:
        checks = [c for c in self._checks
                  if c.connector_id == connector_id and c.status != HealthStatus.DOWN]
        if not checks:
            return 0.0
        return round(sum(c.response_time_ms for c in checks) / len(checks), 1)

    def check_sla(self, connector_id: str, target_uptime: float = 99.9) -> dict:
        uptime = self.get_uptime(connector_id)
        meets_sla = uptime["uptime_percent"] >= target_uptime
        return {
            "target": target_uptime,
            "actual": uptime["uptime_percent"],
            "meets_sla": meets_sla,
            "gap": round(target_uptime - uptime["uptime_percent"], 2) if not meets_sla else 0,
        }
