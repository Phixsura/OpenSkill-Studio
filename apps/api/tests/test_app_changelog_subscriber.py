"""Tests for App Changelog Subscriber — subscribe, notify, filter."""

import pytest

from app.services.app_changelog_subscriber import AppChangelogSubscriber


class TestSubscribe:
    def test_subscribe(self):
        s = AppChangelogSubscriber()
        sub = s.subscribe("inst-1", "sub-1", "email", "user@example.com")
        assert sub.subscriber_id == "sub-1"
        assert sub.active is True

    def test_with_release_types(self):
        s = AppChangelogSubscriber()
        sub = s.subscribe("inst-1", "sub-1", "webhook", "https://x.com",
                          release_types=["major", "security"])
        assert sub.release_types == ["major", "security"]

    def test_duplicate(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "sub-1", "email", "a@b.com")
        with pytest.raises(ValueError, match="already exists"):
            s.subscribe("inst-1", "sub-1", "email", "c@d.com")

    def test_missing_target(self):
        s = AppChangelogSubscriber()
        with pytest.raises(ValueError, match="target"):
            s.subscribe("inst-1", "sub-1", "email", "")


class TestUnsubscribe:
    def test_unsubscribe(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "sub-1", "email", "a@b.com")
        s.unsubscribe("inst-1", "sub-1")
        sub = s.get_subscriber("inst-1", "sub-1")
        assert sub.active is False

    def test_unknown(self):
        s = AppChangelogSubscriber()
        with pytest.raises(KeyError):
            s.unsubscribe("inst-1", "nope")


class TestNotify:
    def test_notify_all(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "sub-1", "email", "a@b.com")
        s.subscribe("inst-1", "sub-2", "webhook", "https://x.com")
        result = s.notify_release("inst-1", "2.0.0", now=1000.0)
        assert len(result.notified) == 2
        assert result.release_version == "2.0.0"

    def test_skips_inactive(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "sub-1", "email", "a@b.com")
        s.unsubscribe("inst-1", "sub-1")
        result = s.notify_release("inst-1", "2.0.0")
        assert len(result.notified) == 0
        assert len(result.skipped) == 1

    def test_filters_by_release_type(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "sub-1", "email", "a@b.com", release_types=["major"])
        result = s.notify_release("inst-1", "1.1.0", release_type="minor")
        assert len(result.notified) == 0
        assert len(result.skipped) == 1

    def test_tracks_notification_count(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "sub-1", "email", "a@b.com")
        s.notify_release("inst-1", "1.0.0", now=1000.0)
        s.notify_release("inst-1", "1.1.0", now=1001.0)
        sub = s.get_subscriber("inst-1", "sub-1")
        assert sub.notification_count == 2
        assert sub.last_notified_at == 1001.0


class TestListSubscribers:
    def test_active_only(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "sub-1", "email", "a@b.com")
        s.subscribe("inst-1", "sub-2", "email", "c@d.com")
        s.unsubscribe("inst-1", "sub-2")
        subs = s.list_subscribers("inst-1")
        assert len(subs) == 1

    def test_include_inactive(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "sub-1", "email", "a@b.com")
        s.subscribe("inst-1", "sub-2", "email", "c@d.com")
        s.unsubscribe("inst-1", "sub-2")
        subs = s.list_subscribers("inst-1", active_only=False)
        assert len(subs) == 2


class TestIsolation:
    def test_cross_installation(self):
        s = AppChangelogSubscriber()
        s.subscribe("inst-1", "sub-1", "email", "a@b.com")
        result = s.notify_release("inst-2", "1.0.0")
        assert len(result.notified) == 0
