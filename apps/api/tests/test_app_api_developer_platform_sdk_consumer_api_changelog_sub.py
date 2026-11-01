"""Tests for Consumer API Changelog Subscriber service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_changelog_sub import (
    ChangelogSubscriptionManager, ChangelogSubscriber,
)


class TestChangelogSubscriptionManager:
    def test_subscribe(self):
        svc = ChangelogSubscriptionManager()
        result = svc.subscribe(ChangelogSubscriber("s1", "c1", "dev@acme.com"))
        assert result["email"] == "dev@acme.com"

    def test_notify_breaking(self):
        svc = ChangelogSubscriptionManager()
        svc.subscribe(ChangelogSubscriber("s1", "c1", "a@b.com", notify_breaking=True))
        svc.subscribe(ChangelogSubscriber("s2", "c2", "c@d.com", notify_breaking=False))
        result = svc.notify("2.0.0", "removed", "Removed v1 endpoints", breaking=True)
        assert result["sent_to"] == 1

    def test_notify_new_features(self):
        svc = ChangelogSubscriptionManager()
        svc.subscribe(ChangelogSubscriber("s1", "c1", "a@b.com", notify_new_features=True))
        result = svc.notify("1.5.0", "added", "New search endpoint")
        assert result["sent_to"] == 1

    def test_notify_deprecation(self):
        svc = ChangelogSubscriptionManager()
        svc.subscribe(ChangelogSubscriber("s1", "c1", "a@b.com", notify_deprecation=True))
        svc.subscribe(ChangelogSubscriber("s2", "c2", "c@d.com", notify_deprecation=False))
        result = svc.notify("1.4.0", "deprecated", "v1 users deprecated")
        assert result["sent_to"] == 1

    def test_inactive_skipped(self):
        svc = ChangelogSubscriptionManager()
        svc.subscribe(ChangelogSubscriber("s1", "c1", "a@b.com", active=False))
        result = svc.notify("1.0.0", "added", "New feature")
        assert result["sent_to"] == 0

    def test_unsubscribe(self):
        svc = ChangelogSubscriptionManager()
        svc.subscribe(ChangelogSubscriber("s1", "c1", "a@b.com"))
        assert svc.unsubscribe("s1")["unsubscribed"] is True
        assert svc.list_subscribers() == []

    def test_update_preferences(self):
        svc = ChangelogSubscriptionManager()
        svc.subscribe(ChangelogSubscriber("s1", "c1", "a@b.com"))
        svc.update_preferences("s1", notify_breaking=False)
        sub = svc.get_subscriber("s1")
        assert sub["notify_breaking"] is False

    def test_notification_history(self):
        svc = ChangelogSubscriptionManager()
        svc.subscribe(ChangelogSubscriber("s1", "c1", "a@b.com"))
        svc.notify("1.0.0", "added", "Feature A")
        svc.notify("1.1.0", "fixed", "Bug fix")
        history = svc.get_notification_history()
        assert len(history) == 2

    def test_invalid_email(self):
        svc = ChangelogSubscriptionManager()
        with pytest.raises(ValueError):
            svc.subscribe(ChangelogSubscriber("s1", "c1", "not-email"))

    def test_duplicate_subscriber(self):
        svc = ChangelogSubscriptionManager()
        svc.subscribe(ChangelogSubscriber("s1", "c1", "a@b.com"))
        with pytest.raises(ValueError):
            svc.subscribe(ChangelogSubscriber("s1", "c2", "c@d.com"))

    def test_stats(self):
        svc = ChangelogSubscriptionManager()
        svc.subscribe(ChangelogSubscriber("s1", "c1", "a@b.com"))
        svc.notify("1.0.0", "added", "New")
        stats = svc.get_stats()
        assert stats["total_subscribers"] == 1
        assert stats["total_notifications"] == 1

    def test_isolation(self):
        a, b = ChangelogSubscriptionManager(), ChangelogSubscriptionManager()
        a.subscribe(ChangelogSubscriber("s1", "c1", "a@b.com"))
        assert b.list_subscribers() == []
