"""Tests for App Feature Flag Audit — record, query, retention."""

import pytest

from app.services.app_feature_flag_audit import AppFeatureFlagAudit


class TestRecord:
    def test_record(self):
        a = AppFeatureFlagAudit()
        e = a.record("inst-1", "e1", "dark_mode", "created", "alice")
        assert e.flag_key == "dark_mode"
        assert e.action == "created"

    def test_invalid_action(self):
        a = AppFeatureFlagAudit()
        with pytest.raises(ValueError, match="Invalid action"):
            a.record("inst-1", "e1", "flag", "bogus", "alice")

    def test_missing_actor(self):
        a = AppFeatureFlagAudit()
        with pytest.raises(ValueError, match="actor"):
            a.record("inst-1", "e1", "flag", "created", "")


class TestQuery:
    def test_by_flag(self):
        a = AppFeatureFlagAudit()
        a.record("inst-1", "e1", "dark_mode", "created", "alice")
        a.record("inst-1", "e2", "dark_mode", "enabled", "bob")
        a.record("inst-1", "e3", "beta_ui", "created", "alice")
        assert len(a.by_flag("inst-1", "dark_mode")) == 2

    def test_by_actor(self):
        a = AppFeatureFlagAudit()
        a.record("inst-1", "e1", "f1", "created", "alice")
        a.record("inst-1", "e2", "f2", "created", "bob")
        a.record("inst-1", "e3", "f3", "enabled", "alice")
        assert len(a.by_actor("inst-1", "alice")) == 2

    def test_recent(self):
        a = AppFeatureFlagAudit()
        for i in range(5):
            a.record("inst-1", f"e{i}", "flag", "enabled", "alice")
        recent = a.recent("inst-1", limit=3)
        assert len(recent) == 3
        assert recent[0].entry_id == "e4"


class TestRetention:
    def test_max_entries(self):
        a = AppFeatureFlagAudit(max_entries=3)
        for i in range(5):
            a.record("inst-1", f"e{i}", "flag", "enabled", "alice")
        assert a.count("inst-1") == 3


class TestIsolation:
    def test_cross(self):
        a = AppFeatureFlagAudit()
        a.record("inst-1", "e1", "flag", "created", "alice")
        assert a.count("inst-2") == 0
