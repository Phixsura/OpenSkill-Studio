"""Tests for Consumer Notification Preferences service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_notif_prefs import NotifPrefsManager


class TestNotifPrefsManager:
    def test_set_and_check(self):
        svc = NotifPrefsManager()
        svc.set_channel("c1", "incident", "email", True, "a@b.com")
        result = svc.should_notify("c1", "incident", "email")
        assert result["notify"] is True
        assert result["destination"] == "a@b.com"

    def test_disable_channel(self):
        svc = NotifPrefsManager()
        svc.set_channel("c1", "billing", "sms", False)
        result = svc.should_notify("c1", "billing", "sms")
        assert result["notify"] is False
        assert result["reason"] == "channel_disabled"

    def test_mute_event(self):
        svc = NotifPrefsManager()
        svc.set_channel("c1", "maintenance", "email", True)
        svc.mute_event("c1", "maintenance", True)
        result = svc.should_notify("c1", "maintenance", "email")
        assert result["notify"] is False
        assert result["reason"] == "event_muted"

    def test_unmute(self):
        svc = NotifPrefsManager()
        svc.mute_event("c1", "security", True)
        svc.mute_event("c1", "security", False)
        result = svc.should_notify("c1", "security", "email")
        assert result["notify"] is True

    def test_default_on(self):
        svc = NotifPrefsManager()
        result = svc.should_notify("c1", "incident", "email")
        assert result["notify"] is True
        assert "defaults" in result["reason"]

    def test_get_preferences(self):
        svc = NotifPrefsManager()
        svc.set_channel("c1", "incident", "email", True)
        svc.set_channel("c1", "incident", "slack", False)
        prefs = svc.get_preferences("c1")
        assert len(prefs) == 6  # all event types
        incident_pref = next(p for p in prefs if p["event_type"] == "incident")
        assert "email" in incident_pref["channels"]

    def test_active_channels(self):
        svc = NotifPrefsManager()
        svc.set_channel("c1", "billing", "email", True)
        svc.set_channel("c1", "billing", "sms", False)
        svc.set_channel("c1", "billing", "slack", True)
        active = svc.get_active_channels("c1", "billing")
        assert "email" in active
        assert "slack" in active
        assert "sms" not in active

    def test_invalid_channel(self):
        svc = NotifPrefsManager()
        with pytest.raises(ValueError):
            svc.set_channel("c1", "incident", "pigeon")

    def test_invalid_event_type(self):
        svc = NotifPrefsManager()
        with pytest.raises(ValueError):
            svc.set_channel("c1", "apocalypse", "email")

    def test_reset(self):
        svc = NotifPrefsManager()
        svc.set_channel("c1", "incident", "email")
        svc.reset("c1")
        result = svc.should_notify("c1", "incident", "email")
        assert "defaults" in result["reason"]

    def test_isolation(self):
        a, b = NotifPrefsManager(), NotifPrefsManager()
        a.set_channel("c1", "incident", "email", False)
        assert b.should_notify("c1", "incident", "email")["notify"] is True
