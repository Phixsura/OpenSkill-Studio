"""Tests for App Resource Quota — consume, release, check, exceed."""

import pytest

from app.services.app_resource_quota import AppResourceQuota


class TestSetQuota:
    def test_set(self):
        q = AppResourceQuota()
        quota = q.set_quota("inst-1", "storage_gb", 100)
        assert quota.limit == 100
        assert quota.used == 0

    def test_invalid_limit(self):
        q = AppResourceQuota()
        with pytest.raises(ValueError, match="positive"):
            q.set_quota("inst-1", "x", 0)

    def test_update_preserves_usage(self):
        q = AppResourceQuota()
        q.set_quota("inst-1", "storage_gb", 100)
        q.consume("inst-1", "storage_gb", 30)
        q.set_quota("inst-1", "storage_gb", 200)
        assert q.get_quota("inst-1", "storage_gb").used == 30


class TestConsume:
    def test_consume(self):
        q = AppResourceQuota()
        q.set_quota("inst-1", "storage_gb", 100)
        quota = q.consume("inst-1", "storage_gb", 25)
        assert quota.used == 25
        assert quota.remaining == 75

    def test_exceed_raises(self):
        q = AppResourceQuota()
        q.set_quota("inst-1", "storage_gb", 10)
        with pytest.raises(ValueError, match="exceed"):
            q.consume("inst-1", "storage_gb", 11)

    def test_negative_amount(self):
        q = AppResourceQuota()
        q.set_quota("inst-1", "x", 10)
        with pytest.raises(ValueError, match="positive"):
            q.consume("inst-1", "x", -1)


class TestRelease:
    def test_release(self):
        q = AppResourceQuota()
        q.set_quota("inst-1", "storage_gb", 100)
        q.consume("inst-1", "storage_gb", 50)
        quota = q.release("inst-1", "storage_gb", 20)
        assert quota.used == 30

    def test_release_below_zero(self):
        q = AppResourceQuota()
        q.set_quota("inst-1", "x", 10)
        q.consume("inst-1", "x", 3)
        quota = q.release("inst-1", "x", 10)
        assert quota.used == 0


class TestCanConsume:
    def test_can(self):
        q = AppResourceQuota()
        q.set_quota("inst-1", "x", 100)
        assert q.can_consume("inst-1", "x", 50) is True

    def test_cannot(self):
        q = AppResourceQuota()
        q.set_quota("inst-1", "x", 10)
        q.consume("inst-1", "x", 8)
        assert q.can_consume("inst-1", "x", 5) is False

    def test_no_quota(self):
        q = AppResourceQuota()
        assert q.can_consume("inst-1", "nope", 1) is False


class TestProperties:
    def test_usage_pct(self):
        q = AppResourceQuota()
        q.set_quota("inst-1", "x", 200)
        q.consume("inst-1", "x", 100)
        assert q.get_quota("inst-1", "x").usage_pct == 50.0

    def test_exceeded(self):
        q = AppResourceQuota()
        q.set_quota("inst-1", "x", 10)
        q.consume("inst-1", "x", 10)
        assert q.get_quota("inst-1", "x").exceeded is True


class TestReset:
    def test_reset(self):
        q = AppResourceQuota()
        q.set_quota("inst-1", "x", 100)
        q.consume("inst-1", "x", 50)
        q.reset_usage("inst-1", "x")
        assert q.get_quota("inst-1", "x").used == 0


class TestIsolation:
    def test_cross_installation(self):
        q = AppResourceQuota()
        q.set_quota("inst-1", "x", 100)
        with pytest.raises(KeyError):
            q.get_quota("inst-2", "x")
