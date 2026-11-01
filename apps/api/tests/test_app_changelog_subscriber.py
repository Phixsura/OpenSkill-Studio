"""Tests for App Changelog Subscriber — subscribe, unsubscribe, delivery."""

import pytest

from app.services.app_changelog_subscriber import AppChangelogSubscriber


class TestSubscribe:
    def test_subscribe(self):
        s = AppChangelogSubscriber()
        sub = s.subscribe("inst-1", "s1", "alice@example.com", "Alice")
        assert sub.active is True

    def test_invalid_email(self):
        s = AppChangelogSubscriber()
        with pytest.raises(ValueError, match="email"):
            s.subscribe("inst-1", "s1", "not-an-email")

    def test_duplicate_email(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "s1", "alice@example.com")
        with pytest.raises(ValueError, match="already subscribed"):
            s.subscribe("inst-1", "s2", "alice@example.com")


class TestUnsubscribe:
    def test_unsubscribe(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "s1", "alice@example.com")
        sub = s.unsubscribe("inst-1", "s1")
        assert sub.active is False
        assert s.count("inst-1") == 0


class TestDelivery:
    def test_record(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "s1", "alice@example.com")
        sub = s.record_delivery("inst-1", "s1")
        assert sub.delivery_count == 1


class TestIsolation:
    def test_cross(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "s1", "alice@example.com")
        assert s.count("inst-2") == 0
