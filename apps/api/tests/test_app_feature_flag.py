"""Tests for App Feature Flag Manager — evaluation, rollout, overrides, audit."""

import pytest

from app.services.app_feature_flag import AppFeatureFlagManager


class TestCreateFlag:
    def test_create(self):
        m = AppFeatureFlagManager()
        f = m.create_flag("inst-1", "dark-mode", enabled=True, description="Dark mode toggle")
        assert f.flag_id == "dark-mode"
        assert f.enabled is True

    def test_duplicate(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1")
        with pytest.raises(ValueError, match="already exists"):
            m.create_flag("inst-1", "f1")

    def test_missing_flag_id(self):
        m = AppFeatureFlagManager()
        with pytest.raises(ValueError, match="flag_id"):
            m.create_flag("inst-1", "")

    def test_invalid_rollout(self):
        m = AppFeatureFlagManager()
        with pytest.raises(ValueError, match="rollout_pct"):
            m.create_flag("inst-1", "f1", rollout_pct=101)


class TestEvaluate:
    def test_unknown_flag_returns_false(self):
        m = AppFeatureFlagManager()
        e = m.evaluate("inst-1", "unknown")
        assert e.enabled is False
        assert e.reason == "default"

    def test_disabled_flag(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1", enabled=False)
        e = m.evaluate("inst-1", "f1", user_id="user-1")
        assert e.enabled is False
        assert e.reason == "global"

    def test_enabled_flag_no_rollout(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1", enabled=True)
        e = m.evaluate("inst-1", "f1", user_id="user-1")
        assert e.enabled is True
        assert e.reason == "global"

    def test_100_pct_rollout(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1", enabled=True, rollout_pct=100)
        e = m.evaluate("inst-1", "f1", user_id="user-1")
        assert e.enabled is True
        assert e.reason == "rollout"

    def test_rollout_deterministic(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1", enabled=True, rollout_pct=50)
        r1 = m.evaluate("inst-1", "f1", user_id="user-A")
        r2 = m.evaluate("inst-1", "f1", user_id="user-A")
        assert r1.enabled == r2.enabled  # stable for same user


class TestOverrides:
    def test_force_enable(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1", enabled=False)
        m.add_override("inst-1", "f1", "user-1", enable=True)
        e = m.evaluate("inst-1", "f1", user_id="user-1")
        assert e.enabled is True
        assert e.reason == "force_enable"

    def test_force_disable(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1", enabled=True)
        m.add_override("inst-1", "f1", "user-1", enable=False)
        e = m.evaluate("inst-1", "f1", user_id="user-1")
        assert e.enabled is False
        assert e.reason == "force_disable"

    def test_override_switches_list(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1", enabled=True)
        m.add_override("inst-1", "f1", "user-1", enable=False)
        m.add_override("inst-1", "f1", "user-1", enable=True)
        f = m._get("inst-1", "f1")
        assert "user-1" in f.force_enable
        assert "user-1" not in f.force_disable


class TestToggle:
    def test_toggle(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1", enabled=False)
        m.toggle("inst-1", "f1", True)
        e = m.evaluate("inst-1", "f1")
        assert e.enabled is True

    def test_toggle_records_change(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1", enabled=False)
        m.toggle("inst-1", "f1", True)
        changes = m.get_changes("inst-1", flag_id="f1")
        assert len(changes) == 1
        assert changes[0].old_value is False
        assert changes[0].new_value is True
        assert changes[0].installation_id == "inst-1"

    def test_changes_scoped_to_installation(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1", enabled=False)
        m.create_flag("inst-2", "f2", enabled=False)
        m.toggle("inst-1", "f1", True)
        m.toggle("inst-2", "f2", True)
        changes = m.get_changes("inst-1")
        assert len(changes) == 1
        assert changes[0].flag_id == "f1"


class TestRollout:
    def test_set_rollout(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1", enabled=True, rollout_pct=0)
        m.set_rollout("inst-1", "f1", 75)
        f = m._get("inst-1", "f1")
        assert f.rollout_pct == 75

    def test_invalid_rollout(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1")
        with pytest.raises(ValueError):
            m.set_rollout("inst-1", "f1", -1)


class TestListFlags:
    def test_list(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1")
        m.create_flag("inst-1", "f2")
        m.create_flag("inst-2", "f3")
        flags = m.list_flags("inst-1")
        assert len(flags) == 2


class TestIsolation:
    def test_cross_installation(self):
        m = AppFeatureFlagManager()
        m.create_flag("inst-1", "f1", enabled=True)
        e = m.evaluate("inst-2", "f1")
        assert e.enabled is False
        assert e.reason == "default"
