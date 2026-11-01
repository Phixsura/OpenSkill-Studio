"""Tests for App Deploy Lock — acquire, release, concurrent blocking."""

import pytest

from app.services.app_deploy_lock import AppDeployLock


class TestAcquire:
    def test_acquire(self):
        d = AppDeployLock()
        lock = d.acquire("inst-1", "l1", "alice", "v2.0 deploy")
        assert lock.owner == "alice"
        assert lock.is_active is True

    def test_concurrent_blocked(self):
        d = AppDeployLock()
        d.acquire("inst-1", "l1", "alice")
        with pytest.raises(ValueError, match="locked by alice"):
            d.acquire("inst-1", "l2", "bob")


class TestRelease:
    def test_release(self):
        d = AppDeployLock()
        d.acquire("inst-1", "l1", "alice")
        lock = d.release("inst-1", "alice")
        assert lock.released_at is not None
        assert d.is_locked("inst-1") is False

    def test_wrong_owner(self):
        d = AppDeployLock()
        d.acquire("inst-1", "l1", "alice")
        with pytest.raises(ValueError, match="not bob"):
            d.release("inst-1", "bob")


class TestForceRelease:
    def test_force(self):
        d = AppDeployLock()
        d.acquire("inst-1", "l1", "alice")
        lock = d.force_release("inst-1")
        assert lock is not None
        assert d.is_locked("inst-1") is False


class TestExpired:
    def test_expired_allows_new(self):
        d = AppDeployLock()
        d.acquire("inst-1", "l1", "alice", timeout_seconds=0)
        # Lock expired immediately, should allow new
        lock = d.acquire("inst-1", "l2", "bob")
        assert lock.owner == "bob"


class TestHistory:
    def test_history(self):
        d = AppDeployLock()
        d.acquire("inst-1", "l1", "alice", timeout_seconds=0)
        d.acquire("inst-1", "l2", "bob", timeout_seconds=0)
        assert len(d.history("inst-1")) == 2


class TestIsolation:
    def test_cross(self):
        d = AppDeployLock()
        d.acquire("inst-1", "l1", "alice")
        assert d.is_locked("inst-2") is False
