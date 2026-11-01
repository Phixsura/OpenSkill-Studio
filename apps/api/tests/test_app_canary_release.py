"""Tests for App Canary Release — traffic split, promote, rollback, metrics."""

import pytest

from app.services.app_canary_release import AppCanaryRelease, CanaryStatus


class TestCreateRelease:
    def test_create(self):
        c = AppCanaryRelease()
        r = c.create_release("inst-1", "r1", "1.0.0", "1.1.0", traffic_pct=10)
        assert r.traffic_pct == 10
        assert r.status == CanaryStatus.ACTIVE

    def test_same_version(self):
        c = AppCanaryRelease()
        with pytest.raises(ValueError, match="differ"):
            c.create_release("inst-1", "r1", "1.0.0", "1.0.0")

    def test_invalid_traffic(self):
        c = AppCanaryRelease()
        with pytest.raises(ValueError, match="traffic_pct"):
            c.create_release("inst-1", "r1", "1.0.0", "1.1.0", traffic_pct=0)

    def test_duplicate(self):
        c = AppCanaryRelease()
        c.create_release("inst-1", "r1", "1.0.0", "1.1.0")
        with pytest.raises(ValueError, match="already exists"):
            c.create_release("inst-1", "r1", "1.0.0", "1.2.0")


class TestUpdateTraffic:
    def test_increase(self):
        c = AppCanaryRelease()
        c.create_release("inst-1", "r1", "1.0.0", "1.1.0", traffic_pct=5)
        r = c.update_traffic("inst-1", "r1", 25)
        assert r.traffic_pct == 25

    def test_cannot_update_promoted(self):
        c = AppCanaryRelease()
        c.create_release("inst-1", "r1", "1.0.0", "1.1.0")
        c.promote("inst-1", "r1")
        with pytest.raises(ValueError, match="non-active"):
            c.update_traffic("inst-1", "r1", 50)


class TestMetrics:
    def test_record(self):
        c = AppCanaryRelease()
        c.create_release("inst-1", "r1", "1.0.0", "1.1.0")
        r = c.record_metrics("inst-1", "r1",
                              stable_error_rate=1.0, canary_error_rate=2.5,
                              stable_latency_ms=50, canary_latency_ms=65)
        assert r.canary_error_rate == 2.5
        assert r.stable_latency_ms == 50


class TestPromote:
    def test_promote(self):
        c = AppCanaryRelease()
        c.create_release("inst-1", "r1", "1.0.0", "1.1.0")
        r = c.promote("inst-1", "r1")
        assert r.status == CanaryStatus.PROMOTED
        assert r.traffic_pct == 100.0

    def test_cannot_promote_twice(self):
        c = AppCanaryRelease()
        c.create_release("inst-1", "r1", "1.0.0", "1.1.0")
        c.promote("inst-1", "r1")
        with pytest.raises(ValueError):
            c.promote("inst-1", "r1")


class TestRollback:
    def test_rollback(self):
        c = AppCanaryRelease()
        c.create_release("inst-1", "r1", "1.0.0", "1.1.0")
        r = c.rollback("inst-1", "r1")
        assert r.status == CanaryStatus.ROLLED_BACK
        assert r.traffic_pct == 0.0


class TestIsolation:
    def test_cross_installation(self):
        c = AppCanaryRelease()
        c.create_release("inst-1", "r1", "1.0.0", "1.1.0")
        with pytest.raises(KeyError):
            c.get_release("inst-2", "r1")
