"""Tests for App Health Checker — heartbeats, probes, uptime, SLA compliance."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.app_health_checker import (
    AppHealthChecker,
    CONSECUTIVE_FAILURES_DEGRADED,
    CONSECUTIVE_FAILURES_DOWN,
    HEARTBEAT_DEAD_SECONDS,
    HEARTBEAT_TIMEOUT_SECONDS,
    HealthStatus,
    ProbeResult,
    ProbeType,
)


class TestHeartbeat:
    def test_first_heartbeat_sets_healthy(self):
        hc = AppHealthChecker()
        status = hc.record_heartbeat("inst-1")
        assert status == HealthStatus.HEALTHY
        assert hc.get_status("inst-1") == HealthStatus.HEALTHY

    def test_heartbeat_recovers_from_down(self):
        hc = AppHealthChecker()
        # Force down state
        for _ in range(CONSECUTIVE_FAILURES_DOWN):
            hc.record_probe("inst-1", ProbeResult(
                probe_type=ProbeType.LIVENESS, success=False,
                latency_ms=100, error="timeout",
            ))
        assert hc.get_status("inst-1") == HealthStatus.DOWN

        # Heartbeat recovers
        status = hc.record_heartbeat("inst-1")
        assert status == HealthStatus.HEALTHY

    def test_heartbeat_resets_failure_count(self):
        hc = AppHealthChecker()
        hc.record_probe("inst-1", ProbeResult(
            probe_type=ProbeType.LIVENESS, success=False, latency_ms=100, error="err",
        ))
        assert hc._failures.get("inst-1", 0) == 1
        hc.record_heartbeat("inst-1")
        assert hc._failures.get("inst-1", 0) == 0


class TestProbes:
    def test_successful_probe_healthy(self):
        hc = AppHealthChecker()
        hc.record_heartbeat("inst-1")
        status = hc.record_probe("inst-1", ProbeResult(
            probe_type=ProbeType.LIVENESS, success=True,
            latency_ms=25, status_code=200,
        ))
        assert status == HealthStatus.HEALTHY

    def test_consecutive_failures_degrade(self):
        hc = AppHealthChecker()
        hc.record_heartbeat("inst-1")
        for _ in range(CONSECUTIVE_FAILURES_DEGRADED):
            status = hc.record_probe("inst-1", ProbeResult(
                probe_type=ProbeType.LIVENESS, success=False,
                latency_ms=5000, error="Connection refused",
            ))
        assert status == HealthStatus.DEGRADED

    def test_more_failures_go_down(self):
        hc = AppHealthChecker()
        hc.record_heartbeat("inst-1")
        for _ in range(CONSECUTIVE_FAILURES_DOWN):
            status = hc.record_probe("inst-1", ProbeResult(
                probe_type=ProbeType.LIVENESS, success=False,
                latency_ms=5000, error="timeout",
            ))
        assert status == HealthStatus.DOWN

    def test_success_after_failure_recovers(self):
        hc = AppHealthChecker()
        hc.record_heartbeat("inst-1")
        for _ in range(3):
            hc.record_probe("inst-1", ProbeResult(
                probe_type=ProbeType.LIVENESS, success=False,
                latency_ms=100, error="err",
            ))
        assert hc.get_status("inst-1") == HealthStatus.DEGRADED

        status = hc.record_probe("inst-1", ProbeResult(
            probe_type=ProbeType.LIVENESS, success=True, latency_ms=20, status_code=200,
        ))
        assert status == HealthStatus.HEALTHY

    def test_readiness_probe_tracked(self):
        hc = AppHealthChecker()
        hc.record_probe("inst-1", ProbeResult(
            probe_type=ProbeType.READINESS, success=True, latency_ms=10, status_code=200,
        ))
        probes = hc._probes.get("inst-1", [])
        assert len(probes) == 1
        assert probes[0].probe_type == ProbeType.READINESS


class TestHeartbeatStaleness:
    def test_stale_heartbeat_degrades(self):
        hc = AppHealthChecker()
        hc.record_heartbeat("inst-1")
        # Simulate stale heartbeat
        hc._heartbeats["inst-1"] = datetime.now(UTC) - timedelta(
            seconds=HEARTBEAT_TIMEOUT_SECONDS + 10
        )
        assert hc.get_status("inst-1") == HealthStatus.DEGRADED

    def test_dead_heartbeat_goes_down(self):
        hc = AppHealthChecker()
        hc.record_heartbeat("inst-1")
        hc._heartbeats["inst-1"] = datetime.now(UTC) - timedelta(
            seconds=HEARTBEAT_DEAD_SECONDS + 10
        )
        assert hc.get_status("inst-1") == HealthStatus.DOWN

    def test_unknown_when_no_heartbeat(self):
        hc = AppHealthChecker()
        assert hc.get_status("inst-1") == HealthStatus.UNKNOWN


class TestTimeline:
    def test_status_changes_recorded(self):
        hc = AppHealthChecker()
        hc.record_heartbeat("inst-1")
        for _ in range(CONSECUTIVE_FAILURES_DOWN):
            hc.record_probe("inst-1", ProbeResult(
                probe_type=ProbeType.LIVENESS, success=False, latency_ms=100, error="err",
            ))
        hc.record_heartbeat("inst-1")

        timeline = hc.get_timeline("inst-1")
        assert len(timeline) >= 2  # degraded → down → healthy transitions
        statuses = [e.status for e in timeline]
        assert HealthStatus.HEALTHY in statuses
        assert HealthStatus.DOWN in statuses

    def test_timeline_limit(self):
        hc = AppHealthChecker()
        hc.record_heartbeat("inst-1")
        timeline = hc.get_timeline("inst-1", limit=5)
        assert len(timeline) <= 5

    def test_empty_timeline(self):
        hc = AppHealthChecker()
        assert hc.get_timeline("nonexistent") == []


class TestUptime:
    def _populate_probes(self, hc: AppHealthChecker, installation_id: str,
                         total: int, failures: int):
        now = datetime.now(UTC)
        for i in range(total):
            success = i >= failures
            hc.record_probe(installation_id, ProbeResult(
                probe_type=ProbeType.LIVENESS, success=success,
                latency_ms=25 if success else 5000,
                status_code=200 if success else None,
                error=None if success else "timeout",
                timestamp=now - timedelta(minutes=(total - i)),
            ))

    def test_perfect_uptime(self):
        hc = AppHealthChecker()
        self._populate_probes(hc, "inst-1", total=100, failures=0)
        summary = hc.get_summary("inst-1")
        assert summary.uptime_24h.uptime_pct == 100.0

    def test_some_failures_reduce_uptime(self):
        hc = AppHealthChecker()
        self._populate_probes(hc, "inst-1", total=100, failures=10)
        summary = hc.get_summary("inst-1")
        assert summary.uptime_24h.uptime_pct == 90.0
        assert summary.uptime_24h.downtime_minutes > 0

    def test_no_probes_100_uptime(self):
        hc = AppHealthChecker()
        summary = hc.get_summary("inst-1")
        assert summary.uptime_24h.uptime_pct == 100.0
        assert summary.uptime_24h.total_checks == 0


class TestSLA:
    def test_compliant_sla(self):
        hc = AppHealthChecker()
        now = datetime.now(UTC)
        for i in range(1000):
            hc.record_probe("inst-1", ProbeResult(
                probe_type=ProbeType.LIVENESS, success=True, latency_ms=20,
                status_code=200, timestamp=now - timedelta(minutes=i),
            ))
        summary = hc.get_summary("inst-1")
        assert summary.sla_compliance.compliant is True
        assert summary.sla_compliance.actual_pct == 100.0

    def test_non_compliant_sla(self):
        hc = AppHealthChecker()
        now = datetime.now(UTC)
        # 95% success → below 99.5% SLA
        for i in range(100):
            success = i >= 5
            hc.record_probe("inst-1", ProbeResult(
                probe_type=ProbeType.LIVENESS, success=success, latency_ms=20,
                status_code=200 if success else None,
                error=None if success else "fail",
                timestamp=now - timedelta(minutes=i),
            ))
        summary = hc.get_summary("inst-1")
        assert summary.sla_compliance.compliant is False
        assert summary.sla_compliance.actual_pct == 95.0


class TestSummary:
    def test_summary_fields(self):
        hc = AppHealthChecker()
        hc.record_heartbeat("inst-1")
        summary = hc.get_summary("inst-1")
        assert summary.installation_id == "inst-1"
        assert summary.current_status == HealthStatus.HEALTHY
        assert summary.last_heartbeat_at is not None
        assert summary.consecutive_failures == 0
        assert summary.uptime_24h is not None
        assert summary.uptime_7d is not None
        assert summary.uptime_30d is not None
        assert summary.sla_compliance is not None

    def test_summary_unknown_installation(self):
        hc = AppHealthChecker()
        summary = hc.get_summary("nonexistent")
        assert summary.current_status == HealthStatus.UNKNOWN
        assert summary.last_heartbeat_at is None
