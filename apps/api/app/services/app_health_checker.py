"""App Health Checker — monitor installed app health via heartbeats, probes, and SLA tracking.

Provides operational health monitoring for installed developer apps:
- Heartbeat tracking: apps report periodic health signals
- Liveness/readiness probe results
- Uptime calculation (rolling 24h, 7d, 30d windows)
- SLA compliance tracking (99.9%, 99.5%, 99.0%)
- Incident detection: automatic degraded/down classification
- Health timeline for debugging
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


class ProbeType(str, Enum):
    LIVENESS = "liveness"
    READINESS = "readiness"
    STARTUP = "startup"


@dataclass
class ProbeResult:
    """Result of a single health probe."""

    probe_type: ProbeType
    success: bool
    latency_ms: float
    status_code: int | None = None
    error: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class HealthEvent:
    """A point-in-time health observation."""

    status: HealthStatus
    timestamp: datetime
    reason: str | None = None
    probe_result: ProbeResult | None = None


@dataclass
class UptimeWindow:
    """Uptime stats for a time window."""

    window_hours: int
    total_checks: int
    successful_checks: int
    uptime_pct: float
    downtime_minutes: float


@dataclass
class SLACompliance:
    """SLA compliance status."""

    target_pct: float  # e.g. 99.9
    actual_pct: float
    compliant: bool
    budget_remaining_minutes: float  # downtime budget left in period
    period_days: int


@dataclass
class AppHealthSummary:
    """Complete health summary for an installed app."""

    installation_id: str
    current_status: HealthStatus
    last_heartbeat_at: datetime | None
    consecutive_failures: int
    uptime_24h: UptimeWindow
    uptime_7d: UptimeWindow
    uptime_30d: UptimeWindow
    sla_compliance: SLACompliance
    recent_events: list[HealthEvent]


# ── Configuration ────────────────────────────────────────

HEARTBEAT_TIMEOUT_SECONDS = 120  # No heartbeat for 2min → degraded
HEARTBEAT_DEAD_SECONDS = 300     # No heartbeat for 5min → down
CONSECUTIVE_FAILURES_DEGRADED = 2
CONSECUTIVE_FAILURES_DOWN = 5
MAX_TIMELINE_EVENTS = 100
DEFAULT_SLA_TARGET = 99.5


class AppHealthChecker:
    """Track health status of installed apps via heartbeats and probes."""

    def __init__(self):
        # installation_id → current status
        self._status: dict[str, HealthStatus] = {}
        # installation_id → last heartbeat time
        self._heartbeats: dict[str, datetime] = {}
        # installation_id → consecutive failure count
        self._failures: dict[str, int] = {}
        # installation_id → timeline (most recent first)
        self._timelines: dict[str, deque[HealthEvent]] = {}
        # installation_id → list of all probe results (for uptime calc)
        self._probes: dict[str, list[ProbeResult]] = {}

    # ── Heartbeat ────────────────────────────────────────

    def record_heartbeat(self, installation_id: str) -> HealthStatus:
        """Record a heartbeat from an installed app."""
        now = datetime.now(UTC)
        self._heartbeats[installation_id] = now

        prev = self._status.get(installation_id, HealthStatus.UNKNOWN)
        if prev in (HealthStatus.DOWN, HealthStatus.DEGRADED, HealthStatus.UNKNOWN):
            self._set_status(installation_id, HealthStatus.HEALTHY, "Heartbeat received — recovered")
        else:
            self._status[installation_id] = HealthStatus.HEALTHY

        self._failures[installation_id] = 0
        return HealthStatus.HEALTHY

    # ── Probes ───────────────────────────────────────────

    def record_probe(self, installation_id: str, result: ProbeResult) -> HealthStatus:
        """Record a liveness/readiness probe result."""
        self._probes.setdefault(installation_id, []).append(result)

        if result.success:
            self._failures[installation_id] = 0
            new_status = HealthStatus.HEALTHY
        else:
            failures = self._failures.get(installation_id, 0) + 1
            self._failures[installation_id] = failures

            if failures >= CONSECUTIVE_FAILURES_DOWN:
                new_status = HealthStatus.DOWN
            elif failures >= CONSECUTIVE_FAILURES_DEGRADED:
                new_status = HealthStatus.DEGRADED
            else:
                new_status = self._status.get(installation_id, HealthStatus.HEALTHY)

        prev = self._status.get(installation_id, HealthStatus.UNKNOWN)
        if new_status != prev:
            reason = (
                f"Probe {'succeeded' if result.success else 'failed'}: "
                f"{result.error or f'HTTP {result.status_code}'}"
            )
            self._set_status(installation_id, new_status, reason, result)

        self._status[installation_id] = new_status
        return new_status

    # ── Status queries ───────────────────────────────────

    def get_status(self, installation_id: str) -> HealthStatus:
        """Get current health status, considering heartbeat staleness."""
        status = self._status.get(installation_id, HealthStatus.UNKNOWN)
        if status == HealthStatus.HEALTHY:
            status = self._check_heartbeat_staleness(installation_id)
        return status

    def get_summary(self, installation_id: str) -> AppHealthSummary:
        """Get complete health summary including uptime and SLA."""
        status = self.get_status(installation_id)
        now = datetime.now(UTC)
        probes = self._probes.get(installation_id, [])
        timeline = list(self._timelines.get(installation_id, deque()))

        return AppHealthSummary(
            installation_id=installation_id,
            current_status=status,
            last_heartbeat_at=self._heartbeats.get(installation_id),
            consecutive_failures=self._failures.get(installation_id, 0),
            uptime_24h=self._compute_uptime(probes, now, 24),
            uptime_7d=self._compute_uptime(probes, now, 168),
            uptime_30d=self._compute_uptime(probes, now, 720),
            sla_compliance=self._compute_sla(probes, now),
            recent_events=timeline[:20],
        )

    def get_timeline(self, installation_id: str, limit: int = 20) -> list[HealthEvent]:
        """Get recent health events."""
        timeline = self._timelines.get(installation_id, deque())
        return list(timeline)[:limit]

    # ── Internals ────────────────────────────────────────

    def _set_status(self, installation_id: str, status: HealthStatus,
                    reason: str, probe: ProbeResult | None = None) -> None:
        prev = self._status.get(installation_id, HealthStatus.UNKNOWN)
        self._status[installation_id] = status

        event = HealthEvent(
            status=status,
            timestamp=datetime.now(UTC),
            reason=reason,
            probe_result=probe,
        )
        timeline = self._timelines.setdefault(
            installation_id, deque(maxlen=MAX_TIMELINE_EVENTS)
        )
        timeline.appendleft(event)

        if status == HealthStatus.DOWN:
            log.warning("app.health_down", installation_id=installation_id, reason=reason)
        elif status == HealthStatus.DEGRADED:
            log.warning("app.health_degraded", installation_id=installation_id, reason=reason)
        elif prev != HealthStatus.HEALTHY and status == HealthStatus.HEALTHY:
            log.info("app.health_recovered", installation_id=installation_id, reason=reason)

    def _check_heartbeat_staleness(self, installation_id: str) -> HealthStatus:
        last = self._heartbeats.get(installation_id)
        if last is None:
            return HealthStatus.UNKNOWN

        age = (datetime.now(UTC) - last).total_seconds()
        if age > HEARTBEAT_DEAD_SECONDS:
            if self._status.get(installation_id) != HealthStatus.DOWN:
                self._set_status(installation_id, HealthStatus.DOWN,
                                 f"No heartbeat for {int(age)}s")
            return HealthStatus.DOWN
        elif age > HEARTBEAT_TIMEOUT_SECONDS:
            if self._status.get(installation_id) != HealthStatus.DEGRADED:
                self._set_status(installation_id, HealthStatus.DEGRADED,
                                 f"Heartbeat stale ({int(age)}s)")
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    @staticmethod
    def _compute_uptime(probes: list[ProbeResult], now: datetime, hours: int) -> UptimeWindow:
        cutoff = now - timedelta(hours=hours)
        window_probes = [p for p in probes if p.timestamp >= cutoff]
        total = len(window_probes)
        if total == 0:
            return UptimeWindow(
                window_hours=hours, total_checks=0,
                successful_checks=0, uptime_pct=100.0, downtime_minutes=0.0,
            )
        successful = sum(1 for p in window_probes if p.success)
        uptime_pct = (successful / total) * 100
        downtime_pct = 100 - uptime_pct
        downtime_minutes = (hours * 60) * (downtime_pct / 100)

        return UptimeWindow(
            window_hours=hours,
            total_checks=total,
            successful_checks=successful,
            uptime_pct=round(uptime_pct, 3),
            downtime_minutes=round(downtime_minutes, 1),
        )

    @staticmethod
    def _compute_sla(probes: list[ProbeResult], now: datetime,
                     target_pct: float = DEFAULT_SLA_TARGET,
                     period_days: int = 30) -> SLACompliance:
        cutoff = now - timedelta(days=period_days)
        window = [p for p in probes if p.timestamp >= cutoff]
        total = len(window)
        if total == 0:
            return SLACompliance(
                target_pct=target_pct, actual_pct=100.0, compliant=True,
                budget_remaining_minutes=period_days * 24 * 60 * (1 - target_pct / 100),
                period_days=period_days,
            )

        successful = sum(1 for p in window if p.success)
        actual_pct = (successful / total) * 100
        total_minutes = period_days * 24 * 60
        allowed_downtime = total_minutes * (1 - target_pct / 100)
        actual_downtime = total_minutes * (1 - actual_pct / 100)
        budget_remaining = max(0.0, allowed_downtime - actual_downtime)

        return SLACompliance(
            target_pct=target_pct,
            actual_pct=round(actual_pct, 3),
            compliant=actual_pct >= target_pct,
            budget_remaining_minutes=round(budget_remaining, 1),
            period_days=period_days,
        )
