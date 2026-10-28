"""Tests for App Health Check Manager — probes, results, availability."""

import pytest

from app.services.app_health_check import (
    AppHealthCheckManager,
    CheckResult,
    ProbeType,
)


class TestRegisterProbe:
    def test_register(self):
        m = AppHealthCheckManager()
        p = m.register_probe("inst-1", "probe-1", "https://api.example.com/health")
        assert p.probe_id == "probe-1"
        assert p.probe_type == ProbeType.HTTP
        assert p.interval_seconds == 30

    def test_missing_installation_id(self):
        m = AppHealthCheckManager()
        with pytest.raises(ValueError, match="installation_id"):
            m.register_probe("", "probe-1", "/health")

    def test_missing_endpoint(self):
        m = AppHealthCheckManager()
        with pytest.raises(ValueError, match="endpoint"):
            m.register_probe("inst-1", "probe-1", "")

    def test_invalid_interval(self):
        m = AppHealthCheckManager()
        with pytest.raises(ValueError, match="interval"):
            m.register_probe("inst-1", "probe-1", "/health", interval_seconds=0)


class TestRecordCheck:
    def test_pass_result(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "probe-1", "/health")
        s = m.record_check("inst-1", "probe-1", CheckResult.PASS, latency_ms=42.0)
        assert s.healthy is True
        assert s.consecutive_failures == 0
        assert s.total_checks == 1

    def test_fail_result(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "probe-1", "/health")
        s = m.record_check("inst-1", "probe-1", CheckResult.FAIL)
        assert s.consecutive_failures == 1

    def test_timeout_result(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "probe-1", "/health")
        s = m.record_check("inst-1", "probe-1", CheckResult.TIMEOUT, message="5s exceeded")
        assert s.consecutive_failures == 1
        assert s.last_check is not None
        assert s.last_check.message == "5s exceeded"

    def test_unknown_probe_raises(self):
        m = AppHealthCheckManager()
        with pytest.raises(KeyError):
            m.record_check("inst-1", "nope", CheckResult.PASS)


class TestHealthStatus:
    def test_healthy_below_threshold(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "probe-1", "/health", failure_threshold=3)
        m.record_check("inst-1", "probe-1", CheckResult.FAIL)
        m.record_check("inst-1", "probe-1", CheckResult.FAIL)
        s = m.get_status("inst-1", "probe-1")
        assert s.healthy is True  # 2 < 3

    def test_unhealthy_at_threshold(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "probe-1", "/health", failure_threshold=3)
        for _ in range(3):
            m.record_check("inst-1", "probe-1", CheckResult.FAIL)
        s = m.get_status("inst-1", "probe-1")
        assert s.healthy is False

    def test_recovery_resets_consecutive(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "probe-1", "/health", failure_threshold=3)
        m.record_check("inst-1", "probe-1", CheckResult.FAIL)
        m.record_check("inst-1", "probe-1", CheckResult.FAIL)
        m.record_check("inst-1", "probe-1", CheckResult.PASS)
        s = m.get_status("inst-1", "probe-1")
        assert s.healthy is True
        assert s.consecutive_failures == 0

    def test_last_failure_tracked(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "probe-1", "/health")
        m.record_check("inst-1", "probe-1", CheckResult.FAIL, message="connection refused")
        m.record_check("inst-1", "probe-1", CheckResult.PASS)
        s = m.get_status("inst-1", "probe-1")
        assert s.last_failure is not None
        assert s.last_failure.message == "connection refused"


class TestAvailability:
    def test_all_pass(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "probe-1", "/health")
        for _ in range(10):
            m.record_check("inst-1", "probe-1", CheckResult.PASS)
        assert m.get_availability("inst-1", "probe-1") == 100.0

    def test_mixed(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "probe-1", "/health")
        for _ in range(8):
            m.record_check("inst-1", "probe-1", CheckResult.PASS)
        for _ in range(2):
            m.record_check("inst-1", "probe-1", CheckResult.FAIL)
        assert m.get_availability("inst-1", "probe-1") == 80.0

    def test_windowed_availability(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "probe-1", "/health")
        for _ in range(5):
            m.record_check("inst-1", "probe-1", CheckResult.FAIL)
        for _ in range(5):
            m.record_check("inst-1", "probe-1", CheckResult.PASS)
        assert m.get_availability("inst-1", "probe-1", last_n=5) == 100.0

    def test_no_checks_returns_100(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "probe-1", "/health")
        assert m.get_availability("inst-1", "probe-1") == 100.0


class TestProbeManagement:
    def test_list_probes(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "p1", "/health")
        m.register_probe("inst-1", "p2", "/ready")
        m.register_probe("inst-2", "p3", "/health")
        probes = m.list_probes("inst-1")
        assert len(probes) == 2

    def test_remove_probe(self):
        m = AppHealthCheckManager()
        m.register_probe("inst-1", "p1", "/health")
        m.remove_probe("inst-1", "p1")
        assert len(m.list_probes("inst-1")) == 0

    def test_remove_nonexistent_raises(self):
        m = AppHealthCheckManager()
        with pytest.raises(KeyError):
            m.remove_probe("inst-1", "nope")


class TestHistoryLimit:
    def test_trims_history(self):
        m = AppHealthCheckManager(history_limit=5)
        m.register_probe("inst-1", "p1", "/health")
        for _ in range(10):
            m.record_check("inst-1", "p1", CheckResult.PASS)
        s = m.get_status("inst-1", "p1")
        assert s.total_checks == 5
