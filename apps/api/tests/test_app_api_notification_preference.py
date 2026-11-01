"""Tests for App API Notification Preference — channels, mute, should_notify."""

import pytest
from app.services.app_api_notification_preference import AppAPINotificationPreference


class TestChannels:
    def test_set(self):
        p = AppAPINotificationPreference()
        pref = p.set_channels("inst-1", "user-1", ["email", "slack"])
        assert pref.channels == {"email", "slack"}

    def test_invalid(self):
        p = AppAPINotificationPreference()
        with pytest.raises(ValueError):
            p.set_channels("inst-1", "user-1", ["carrier_pigeon"])


class TestMute:
    def test_mute_unmute(self):
        p = AppAPINotificationPreference()
        p.mute_event("inst-1", "user-1", "marketing")
        assert p.should_notify("inst-1", "user-1", "marketing", "email") is False
        p.unmute_event("inst-1", "user-1", "marketing")
        assert p.should_notify("inst-1", "user-1", "marketing", "email") is True


class TestShouldNotify:
    def test_channel_check(self):
        p = AppAPINotificationPreference()
        p.set_channels("inst-1", "user-1", ["email"])
        assert p.should_notify("inst-1", "user-1", "alert", "email") is True
        assert p.should_notify("inst-1", "user-1", "alert", "slack") is False

    def test_default_notify(self):
        p = AppAPINotificationPreference()
        assert p.should_notify("inst-1", "unknown", "alert", "email") is True


class TestIsolation:
    def test_cross(self):
        p = AppAPINotificationPreference()
        p.mute_event("inst-1", "user-1", "alert")
        assert p.should_notify("inst-2", "user-1", "alert", "email") is True
