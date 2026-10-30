"""Consumer API Webhook Health Monitor — monitor webhook endpoint health."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class HealthCheck:
    check_id: str
    webhook_id: str
    status: str  # "healthy", "degraded", "down"
    response_time_ms: float
    status_code: int | None = None
    error: str | None = None
    checked_at: datetime | None = None

@dataclass
class HealthSummary:
    webhook_id: str
    status: str
    uptime_pct: float
    avg_response_ms: float
    last_check_at: datetime | None = None
    consecutive_failures: int = 0
    total_checks: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookHealthMonitor:
    def __init__(self) -> None:
        self._checks: dict[tuple[str, str, str], list[HealthCheck]] = {}  # (inst, consumer, webhook)

    def record_check(self, installation_id: str, consumer_id: str, check: HealthCheck) -> HealthCheck:
        if not installation_id:
            raise ValueError("installation_id is required")
        check.checked_at = check.checked_at or datetime.utcnow()
        key = (installation_id, consumer_id, check.webhook_id)
        if key not in self._checks:
            self._checks[key] = []
        self._checks[key].append(check)
        if len(self._checks[key]) > 1000:
            self._checks[key] = self._checks[key][-1000:]
        return check

    def get_summary(self, installation_id: str, consumer_id: str, webhook_id: str) -> HealthSummary:
        checks = self._checks.get((installation_id, consumer_id, webhook_id), [])
        if not checks:
            return HealthSummary(webhook_id=webhook_id, status="unknown", uptime_pct=0, avg_response_ms=0, total_checks=0)
        healthy = sum(1 for c in checks if c.status == "healthy")
        uptime = (healthy / len(checks)) * 100
        avg_rt = sum(c.response_time_ms for c in checks if c.status == "healthy") / max(1, healthy)
        # Consecutive failures from end
        consec_fail = 0
        for c in reversed(checks):
            if c.status != "healthy":
                consec_fail += 1
            else:
                break
        if consec_fail >= 3:
            status = "down"
        elif checks[-1].status != "healthy":
            status = "degraded"
        else:
            status = "healthy"
        return HealthSummary(webhook_id=webhook_id, status=status, uptime_pct=round(uptime, 1), avg_response_ms=round(avg_rt, 1), last_check_at=checks[-1].checked_at, consecutive_failures=consec_fail, total_checks=len(checks))

    def list_unhealthy(self, installation_id: str, consumer_id: str) -> list[HealthSummary]:
        result = []
        for (inst, cid, wid) in self._checks:
            if inst != installation_id or cid != consumer_id:
                continue
            summary = self.get_summary(inst, cid, wid)
            if summary.status != "healthy":
                result.append(summary)
        return result
