"""Tests for App Rollback Manager — deploy, rollback, history."""

import pytest

from app.services.app_rollback_manager import AppRollbackManager, RollbackStatus


class TestDeploy:
    def test_record(self):
        r = AppRollbackManager()
        v = r.record_deploy("inst-1", "v1.0")
        assert v.is_current is True

    def test_current_version(self):
        r = AppRollbackManager()
        r.record_deploy("inst-1", "v1.0")
        r.record_deploy("inst-1", "v2.0")
        assert r.current_version("inst-1") == "v2.0"


class TestRollback:
    def test_rollback(self):
        r = AppRollbackManager()
        r.record_deploy("inst-1", "v1.0")
        r.record_deploy("inst-1", "v2.0")
        rec = r.rollback("inst-1", "rb1", "Bug in v2.0", "alice")
        assert rec.from_version == "v2.0"
        assert rec.to_version == "v1.0"
        assert r.current_version("inst-1") == "v1.0"

    def test_no_previous(self):
        r = AppRollbackManager()
        r.record_deploy("inst-1", "v1.0")
        with pytest.raises(ValueError, match="No previous"):
            r.rollback("inst-1", "rb1")

    def test_complete(self):
        r = AppRollbackManager()
        r.record_deploy("inst-1", "v1.0")
        r.record_deploy("inst-1", "v2.0")
        r.rollback("inst-1", "rb1")
        rec = r.complete_rollback("inst-1", "rb1")
        assert rec.status == RollbackStatus.COMPLETED


class TestHistory:
    def test_history(self):
        r = AppRollbackManager()
        r.record_deploy("inst-1", "v1.0")
        r.record_deploy("inst-1", "v2.0")
        r.rollback("inst-1", "rb1", "Bug")
        assert len(r.rollback_history("inst-1")) == 1


class TestIsolation:
    def test_cross(self):
        r = AppRollbackManager()
        r.record_deploy("inst-1", "v1.0")
        assert r.current_version("inst-2") is None
