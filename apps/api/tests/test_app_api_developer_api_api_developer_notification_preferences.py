import pytest
from app.services.app_api_developer_api_api_developer_notification_preferences import AppAPIDeveloperAPIApiDeveloperNotificationPreferences

class TestNotificationPreferences:
    def test_defaults(self):
        p = AppAPIDeveloperAPIApiDeveloperNotificationPreferences()
        pref = p.get_or_create("inst-1", "dev1")
        assert "email" in pref.enabled_channels
        assert "incident" in pref.enabled_categories

    def test_set_channels(self):
        p = AppAPIDeveloperAPIApiDeveloperNotificationPreferences()
        p.set_channels("inst-1", "dev1", ["slack", "webhook"])
        pref = p.get_or_create("inst-1", "dev1")
        assert pref.enabled_channels == {"slack", "webhook"}

    def test_invalid_channel(self):
        p = AppAPIDeveloperAPIApiDeveloperNotificationPreferences()
        with pytest.raises(ValueError):
            p.set_channels("inst-1", "dev1", ["sms"])

    def test_should_notify(self):
        p = AppAPIDeveloperAPIApiDeveloperNotificationPreferences()
        p.set_channels("inst-1", "dev1", ["email"])
        p.set_categories("inst-1", "dev1", ["incident"])
        assert p.should_notify("inst-1", "dev1", "incident", "email") is True
        assert p.should_notify("inst-1", "dev1", "changelog", "email") is False
        assert p.should_notify("inst-1", "dev1", "incident", "slack") is False

    def test_quiet_hours(self):
        p = AppAPIDeveloperAPIApiDeveloperNotificationPreferences()
        pref = p.set_quiet_hours("inst-1", "dev1", 22, 8)
        assert pref.quiet_hours_start == 22
