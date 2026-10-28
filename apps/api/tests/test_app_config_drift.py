"""Tests for App Config Drift — snapshot, compare, drift detection."""

import pytest

from app.services.app_config_drift import AppConfigDrift


STAGING = {"DB_HOST": "staging-db", "REDIS_URL": "redis://staging", "LOG_LEVEL": "debug"}
PROD = {"DB_HOST": "prod-db", "REDIS_URL": "redis://prod", "LOG_LEVEL": "info", "SENTRY_DSN": "https://sentry"}


class TestSnapshot:
    def test_snapshot(self):
        d = AppConfigDrift()
        cfg = d.snapshot("inst-1", "staging", STAGING)
        assert cfg["DB_HOST"] == "staging-db"

    def test_list_envs(self):
        d = AppConfigDrift()
        d.snapshot("inst-1", "staging", STAGING)
        d.snapshot("inst-1", "prod", PROD)
        assert d.list_envs("inst-1") == ["prod", "staging"]


class TestCompare:
    def test_detect_changed(self):
        d = AppConfigDrift()
        d.snapshot("inst-1", "staging", STAGING)
        d.snapshot("inst-1", "prod", PROD)
        report = d.compare("inst-1", "staging", "prod")
        changed = [e for e in report.drifts if e.drift_type == "changed"]
        keys = [e.key for e in changed]
        assert "DB_HOST" in keys
        assert "LOG_LEVEL" in keys

    def test_detect_added(self):
        d = AppConfigDrift()
        d.snapshot("inst-1", "staging", STAGING)
        d.snapshot("inst-1", "prod", PROD)
        report = d.compare("inst-1", "staging", "prod")
        added = [e for e in report.drifts if e.drift_type == "added"]
        assert any(e.key == "SENTRY_DSN" for e in added)

    def test_no_drift(self):
        d = AppConfigDrift()
        d.snapshot("inst-1", "a", {"X": "1"})
        d.snapshot("inst-1", "b", {"X": "1"})
        report = d.compare("inst-1", "a", "b")
        assert report.has_drift is False

    def test_missing_env(self):
        d = AppConfigDrift()
        d.snapshot("inst-1", "staging", STAGING)
        with pytest.raises(KeyError):
            d.compare("inst-1", "staging", "prod")


class TestIsolation:
    def test_cross(self):
        d = AppConfigDrift()
        d.snapshot("inst-1", "staging", STAGING)
        assert d.list_envs("inst-2") == []
