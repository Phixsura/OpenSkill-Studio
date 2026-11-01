"""Tests for App Notification Preference — channels, mute, quiet hours."""

import pytest

from app.services.app_notification_preference import AppNotificationPreference


class TestGetOrCreate:
    def test_create(self):
        p = AppNotificationPreference()
        pref = p.get_or_create("inst-1", "user-1")
        assert pref.user_id == "user-1"
        assert pref.channels["email"] is True
        assert pref.global_mute is False

    def test_idempotent(self):
        p = AppNotificationPreference()
        p1 = p.get_or_create("inst-1", "user-1")
        p2 = p.get_or_create("inst-1", "user-1")
        assert p1 is p2


class TestChannels:
    def test_disable_channel(self):
        p = AppNotificationPreference()
        pref = p.set_channel("inst-1", "user-1", "email", False)
        assert pref.channels["email"] is False

    def test_invalid_channel(self):
        p = AppNotificationPreference()
        with pytest.raises(ValueError, match="Invalid channel"):
            p.set_channel("inst-1", "user-1", "telegram", True)


class TestCategories:
    def test_mute_category(self):
        p = AppNotificationPreference()
        pref = p.mute_category("inst-1", "user-1", "marketing")
        assert "marketing" in pref.muted_categories

    def test_unmute_category(self):
        p = AppNotificationPreference()
        p.mute_category("inst-1", "user-1", "marketing")
        pref = p.unmute_category("inst-1", "user-1", "marketing")
        assert "marketing" not in pref.muted_categories


class TestGlobalMute:
    def test_mute(self):
        p = AppNotificationPreference()
        pref = p.set_global_mute("inst-1", "user-1", True)
        assert pref.global_mute is True


class TestQuietHours:
    def test_set(self):
        p = AppNotificationPreference()
        pref = p.set_quiet_hours("inst-1", "user-1", 22, 7)
        assert pref.quiet_hours_start == 22
        assert pref.quiet_hours_end == 7

    def test_invalid_hours(self):
        p = AppNotificationPreference()
        with pytest.raises(ValueError, match="Hours"):
            p.set_quiet_hours("inst-1", "user-1", 25, 7)


class TestShouldNotify:
    def test_default_allows(self):
        p = AppNotificationPreference()
        assert p.should_notify("inst-1", "user-1", "email") is True

    def test_global_mute_blocks(self):
        p = AppNotificationPreference()
        p.set_global_mute("inst-1", "user-1", True)
        assert p.should_notify("inst-1", "user-1", "email") is False

    def test_channel_disabled_blocks(self):
        p = AppNotificationPreference()
        p.set_channel("inst-1", "user-1", "push", False)
        assert p.should_notify("inst-1", "user-1", "push") is False

    def test_muted_category_blocks(self):
        p = AppNotificationPreference()
        p.mute_category("inst-1", "user-1", "marketing")
        assert p.should_notify("inst-1", "user-1", "email", category="marketing") is False
        assert p.should_notify("inst-1", "user-1", "email", category="alerts") is True

    def test_quiet_hours_blocks(self):
        p = AppNotificationPreference()
        p.set_quiet_hours("inst-1", "user-1", 22, 7)
        assert p.should_notify("inst-1", "user-1", "email", current_hour=23) is False
        assert p.should_notify("inst-1", "user-1", "email", current_hour=3) is False
        assert p.should_notify("inst-1", "user-1", "email", current_hour=10) is True

    def test_quiet_hours_same_day(self):
        p = AppNotificationPreference()
        p.set_quiet_hours("inst-1", "user-1", 12, 14)
        assert p.should_notify("inst-1", "user-1", "email", current_hour=13) is False
        assert p.should_notify("inst-1", "user-1", "email", current_hour=15) is True


class TestIsolation:
    def test_cross_installation(self):
        p = AppNotificationPreference()
        p.set_global_mute("inst-1", "user-1", True)
        assert p.should_notify("inst-2", "user-1", "email") is True
