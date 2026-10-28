"""Tests for App Rollback Manager — safety checks, lifecycle, history."""

import pytest

from app.services.app_rollback_manager import AppRollbackManager, RollbackStatus


class TestInitiate:
    def test_initiate(self):
        m = AppRollbackManager()
        r = m.initiate_rollback("inst-1", "rb-1", "2.0.0", "1.9.0", "Bug in 2.0", now=1000.0)
        assert r.status == RollbackStatus.PENDING
        assert r.from_version == "2.0.0"
        assert r.to_version == "1.9.0"

    def test_same_version(self):
        m = AppRollbackManager()
        with pytest.raises(ValueError, match="same version"):
            m.initiate_rollback("inst-1", "rb-1", "1.0.0", "1.0.0", "bug")

    def test_missing_reason(self):
        m = AppRollbackManager()
        with pytest.raises(ValueError, match="reason"):
            m.initiate_rollback("inst-1", "rb-1", "2.0", "1.0", "")

    def test_duplicate(self):
        m = AppRollbackManager()
        m.initiate_rollback("inst-1", "rb-1", "2.0", "1.0", "bug", now=1000.0)
        with pytest.raises(ValueError, match="already exists"):
            m.initiate_rollback("inst-1", "rb-1", "2.0", "1.0", "bug2", now=2000.0)


class TestSafetyChecks:
    def test_min_version(self):
        m = AppRollbackManager(min_version="1.0.0")
        with pytest.raises(ValueError, match="minimum version"):
            m.initiate_rollback("inst-1", "rb-1", "2.0.0", "0.9.0", "bug")

    def test_cooldown(self):
        m = AppRollbackManager(cooldown_seconds=60)
        m.initiate_rollback("inst-1", "rb-1", "2.0", "1.0", "bug", now=1000.0)
        with pytest.raises(ValueError, match="cooldown"):
            m.initiate_rollback("inst-1", "rb-2", "2.0", "1.5", "bug2", now=1050.0)

    def test_after_cooldown(self):
        m = AppRollbackManager(cooldown_seconds=60)
        m.initiate_rollback("inst-1", "rb-1", "2.0", "1.0", "bug", now=1000.0)
        r = m.initiate_rollback("inst-1", "rb-2", "2.0", "1.5", "bug2", now=1061.0)
        assert r.rollback_id == "rb-2"


class TestLifecycle:
    def test_full_lifecycle(self):
        m = AppRollbackManager()
        m.initiate_rollback("inst-1", "rb-1", "2.0", "1.0", "bug")
        m.start_rollback("inst-1", "rb-1")
        r = m.complete_rollback("inst-1", "rb-1")
        assert r.status == RollbackStatus.COMPLETED

    def test_fail(self):
        m = AppRollbackManager()
        m.initiate_rollback("inst-1", "rb-1", "2.0", "1.0", "bug")
        m.start_rollback("inst-1", "rb-1")
        r = m.fail_rollback("inst-1", "rb-1", error="timeout")
        assert r.status == RollbackStatus.FAILED
        assert r.error == "timeout"

    def test_cannot_start_completed(self):
        m = AppRollbackManager()
        m.initiate_rollback("inst-1", "rb-1", "2.0", "1.0", "bug")
        m.start_rollback("inst-1", "rb-1")
        m.complete_rollback("inst-1", "rb-1")
        with pytest.raises(ValueError):
            m.start_rollback("inst-1", "rb-1")


class TestHistory:
    def test_newest_first(self):
        m = AppRollbackManager(cooldown_seconds=0)
        m.initiate_rollback("inst-1", "rb-1", "2.0", "1.0", "a", now=1000.0)
        m.initiate_rollback("inst-1", "rb-2", "2.0", "1.5", "b", now=1001.0)
        h = m.get_history("inst-1")
        assert h[0].rollback_id == "rb-2"


class TestIsolation:
    def test_cross_installation(self):
        m = AppRollbackManager()
        m.initiate_rollback("inst-1", "rb-1", "2.0", "1.0", "bug")
        with pytest.raises(KeyError):
            m.get_rollback("inst-2", "rb-1")
