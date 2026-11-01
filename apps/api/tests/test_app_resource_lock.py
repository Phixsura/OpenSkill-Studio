"""Tests for App Resource Lock — acquire, release, expiry, re-entrant."""

import pytest

from app.services.app_resource_lock import AppResourceLock


class TestAcquire:
    def test_acquire(self):
        l = AppResourceLock()
        r = l.acquire("inst-1", "orders/123", "worker-1", now=1000.0)
        assert r.acquired is True
        assert r.owner == "worker-1"

    def test_already_locked(self):
        l = AppResourceLock()
        l.acquire("inst-1", "orders/123", "worker-1", now=1000.0)
        r = l.acquire("inst-1", "orders/123", "worker-2", now=1001.0)
        assert r.acquired is False
        assert r.reason == "already_locked"

    def test_reentrant(self):
        l = AppResourceLock()
        l.acquire("inst-1", "r1", "owner-1", now=1000.0)
        r = l.acquire("inst-1", "r1", "owner-1", now=1005.0)
        assert r.acquired is True

    def test_missing_owner(self):
        l = AppResourceLock()
        with pytest.raises(ValueError, match="owner"):
            l.acquire("inst-1", "r1", "")


class TestRelease:
    def test_release(self):
        l = AppResourceLock()
        l.acquire("inst-1", "r1", "owner-1")
        assert l.release("inst-1", "r1", "owner-1") is True
        assert l.is_locked("inst-1", "r1") is False

    def test_wrong_owner(self):
        l = AppResourceLock()
        l.acquire("inst-1", "r1", "owner-1")
        with pytest.raises(ValueError, match="owner"):
            l.release("inst-1", "r1", "owner-2")

    def test_release_nonexistent(self):
        l = AppResourceLock()
        assert l.release("inst-1", "r1", "owner-1") is False


class TestExpiry:
    def test_expired_lock_reclaimed(self):
        l = AppResourceLock(default_ttl_seconds=10)
        l.acquire("inst-1", "r1", "owner-1", now=1000.0)
        r = l.acquire("inst-1", "r1", "owner-2", now=1011.0)
        assert r.acquired is True
        assert r.reason == "expired_reclaimed"

    def test_not_expired(self):
        l = AppResourceLock(default_ttl_seconds=10)
        l.acquire("inst-1", "r1", "owner-1", now=1000.0)
        assert l.is_locked("inst-1", "r1", now=1005.0) is True

    def test_expired_unlocked(self):
        l = AppResourceLock(default_ttl_seconds=10)
        l.acquire("inst-1", "r1", "owner-1", now=1000.0)
        assert l.is_locked("inst-1", "r1", now=1011.0) is False

    def test_custom_ttl(self):
        l = AppResourceLock(default_ttl_seconds=30)
        l.acquire("inst-1", "r1", "owner-1", ttl_seconds=5, now=1000.0)
        assert l.is_locked("inst-1", "r1", now=1006.0) is False


class TestListLocks:
    def test_list(self):
        l = AppResourceLock()
        l.acquire("inst-1", "r1", "o1")
        l.acquire("inst-1", "r2", "o2")
        l.acquire("inst-2", "r3", "o3")
        locks = l.list_locks("inst-1")
        assert len(locks) == 2


class TestIsolation:
    def test_cross_installation(self):
        l = AppResourceLock()
        l.acquire("inst-1", "r1", "owner-1")
        r = l.acquire("inst-2", "r1", "owner-2")
        assert r.acquired is True  # different installation


class TestConfig:
    def test_invalid_ttl(self):
        with pytest.raises(ValueError):
            AppResourceLock(default_ttl_seconds=0)
