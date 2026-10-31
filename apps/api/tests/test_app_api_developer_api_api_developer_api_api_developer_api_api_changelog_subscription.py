import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_changelog_subscription import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiChangelogSubscription

class TestChangelogSubscription:
    def test_subscribe(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiChangelogSubscription()
        sub = s.subscribe("inst-1", "s1", "dev1", ["email", "slack"], ["breaking"])
        assert sub.active is True

    def test_invalid_channel(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiChangelogSubscription()
        with pytest.raises(ValueError):
            s.subscribe("inst-1", "s1", "dev1", ["sms"])

    def test_notify_filtered(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiChangelogSubscription()
        s.subscribe("inst-1", "s1", "d1", ["email"], ["breaking"])
        s.subscribe("inst-1", "s2", "d2", ["email"], ["feature"])
        matched = s.notify("inst-1", "breaking")
        assert len(matched) == 1

    def test_notify_all(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiChangelogSubscription()
        s.subscribe("inst-1", "s1", "d1", ["email"])  # no filters = all
        matched = s.notify("inst-1", "anything")
        assert len(matched) == 1

    def test_unsubscribe(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiChangelogSubscription()
        s.subscribe("inst-1", "s1", "d1", ["email"])
        s.unsubscribe("inst-1", "s1")
        assert s.active_count("inst-1") == 0

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiChangelogSubscription()
        s.subscribe("inst-1", "s1", "d1", ["email"])
        assert s.active_count("inst-2") == 0
