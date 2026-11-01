"""Tests for App Notification Dispatcher — send, targeting, read/dismiss, rate limit."""

import pytest

from app.services.app_notification_dispatcher import (
    RATE_LIMIT_PER_HOUR,
    AppNotificationDispatcher,
    NotificationPriority,
    TargetType,
)


class TestSend:
    def test_send_basic(self):
        d = AppNotificationDispatcher()
        r = d.send("app-1", "My App", "org-1", "Hello", "World")
        assert r.success is True
        assert r.notification_id is not None

    def test_send_with_priority(self):
        d = AppNotificationDispatcher()
        r = d.send("app-1", "My App", "org-1", "Alert", "Check this",
                    priority=NotificationPriority.ACTION_REQUIRED)
        assert r.success is True

    def test_send_with_action_url(self):
        d = AppNotificationDispatcher()
        r = d.send("app-1", "My App", "org-1", "Click", "Details",
                    action_url="https://example.com/action")
        notif = d._notifications[r.notification_id]
        assert notif.action_url == "https://example.com/action"

    def test_empty_title_rejected(self):
        d = AppNotificationDispatcher()
        r = d.send("app-1", "My App", "org-1", "", "Body")
        assert r.success is False

    def test_long_title_rejected(self):
        d = AppNotificationDispatcher()
        r = d.send("app-1", "My App", "org-1", "T" * 201, "Body")
        assert r.success is False

    def test_long_body_rejected(self):
        d = AppNotificationDispatcher()
        r = d.send("app-1", "My App", "org-1", "Title", "B" * 2001)
        assert r.success is False

    def test_user_target_requires_value(self):
        d = AppNotificationDispatcher()
        r = d.send("app-1", "My App", "org-1", "Hi", "Body",
                    target_type=TargetType.USER, target_value="")
        assert r.success is False


class TestRateLimit:
    def test_rate_limit_enforced(self):
        d = AppNotificationDispatcher()
        for i in range(RATE_LIMIT_PER_HOUR):
            r = d.send("app-1", "App", "org-1", f"Notif {i}", "Body")
            assert r.success is True
        r = d.send("app-1", "App", "org-1", "One more", "Body")
        assert r.success is False
        assert "Rate limit" in r.error

    def test_different_apps_independent(self):
        d = AppNotificationDispatcher()
        for i in range(RATE_LIMIT_PER_HOUR):
            d.send("app-1", "App1", "org-1", f"N{i}", "B")
        # app-2 should still work
        r = d.send("app-2", "App2", "org-1", "Hello", "Body")
        assert r.success is True

    def test_get_rate_usage(self):
        d = AppNotificationDispatcher()
        d.send("app-1", "App", "org-1", "A", "B")
        d.send("app-1", "App", "org-1", "C", "D")
        assert d.get_rate_usage("app-1") == 2


class TestTargeting:
    def test_user_targeting(self):
        d = AppNotificationDispatcher()
        d.send("app-1", "App", "org-1", "For you", "Details",
               target_type=TargetType.USER, target_value="user-1")
        d.send("app-1", "App", "org-1", "For other", "Details",
               target_type=TargetType.USER, target_value="user-2")
        notifs = d.get_for_user("user-1", "org-1")
        assert len(notifs) == 1
        assert notifs[0].title == "For you"

    def test_org_all_targeting(self):
        d = AppNotificationDispatcher()
        d.send("app-1", "App", "org-1", "Everyone", "All",
               target_type=TargetType.ORG_ALL)
        assert len(d.get_for_user("user-1", "org-1")) == 1
        assert len(d.get_for_user("user-2", "org-1")) == 1

    def test_cross_org_isolation(self):
        d = AppNotificationDispatcher()
        d.send("app-1", "App", "org-1", "Org1 only", "Details")
        assert len(d.get_for_user("user-1", "org-2")) == 0


class TestReadDismiss:
    def test_mark_read(self):
        d = AppNotificationDispatcher()
        r = d.send("app-1", "App", "org-1", "Title", "Body")
        assert d.mark_read(r.notification_id, "user-1", "org-1") is True
        notif = d._notifications[r.notification_id]
        assert notif.read is True

    def test_mark_read_nonexistent(self):
        d = AppNotificationDispatcher()
        assert d.mark_read("nonexistent", "user-1", "org-1") is False

    def test_mark_read_wrong_org_blocked(self):
        d = AppNotificationDispatcher()
        r = d.send("app-1", "App", "org-1", "Title", "Body")
        assert d.mark_read(r.notification_id, "user-1", "org-2") is False

    def test_mark_read_wrong_user_blocked(self):
        d = AppNotificationDispatcher()
        r = d.send("app-1", "App", "org-1", "Title", "Body",
                    target_type=TargetType.USER, target_value="user-1")
        assert d.mark_read(r.notification_id, "user-2", "org-1") is False

    def test_dismiss(self):
        d = AppNotificationDispatcher()
        r = d.send("app-1", "App", "org-1", "Title", "Body")
        assert d.dismiss(r.notification_id, "user-1", "org-1") is True
        assert len(d.get_for_user("user-1", "org-1")) == 0

    def test_dismiss_wrong_org_blocked(self):
        d = AppNotificationDispatcher()
        r = d.send("app-1", "App", "org-1", "Title", "Body")
        assert d.dismiss(r.notification_id, "user-1", "org-2") is False

    def test_mark_all_read(self):
        d = AppNotificationDispatcher()
        d.send("app-1", "App", "org-1", "A", "B")
        d.send("app-1", "App", "org-1", "C", "D")
        count = d.mark_all_read("user-1", "org-1")
        assert count == 2
        assert d.unread_count("user-1", "org-1") == 0

    def test_dismiss_all(self):
        d = AppNotificationDispatcher()
        d.send("app-1", "App", "org-1", "A", "B")
        d.send("app-1", "App", "org-1", "C", "D")
        count = d.dismiss_all("user-1", "org-1")
        assert count == 2
        assert len(d.get_for_user("user-1", "org-1")) == 0

    def test_unread_only_filter(self):
        d = AppNotificationDispatcher()
        r1 = d.send("app-1", "App", "org-1", "Read", "B")
        d.send("app-1", "App", "org-1", "Unread", "B")
        d.mark_read(r1.notification_id, "user-1", "org-1")
        unread = d.get_for_user("user-1", "org-1", unread_only=True)
        assert len(unread) == 1
        assert unread[0].title == "Unread"


class TestRoleTargeting:
    def test_role_targeting_with_matching_role(self):
        d = AppNotificationDispatcher()
        d.send("app-1", "App", "org-1", "Admin alert", "Details",
               target_type=TargetType.ROLE, target_value="admin")
        notifs = d.get_for_user("user-1", "org-1", user_roles={"admin", "instructor"})
        assert len(notifs) == 1

    def test_role_targeting_without_matching_role(self):
        d = AppNotificationDispatcher()
        d.send("app-1", "App", "org-1", "Admin alert", "Details",
               target_type=TargetType.ROLE, target_value="admin")
        notifs = d.get_for_user("user-1", "org-1", user_roles={"student"})
        assert len(notifs) == 0

    def test_role_targeting_fail_closed_no_roles(self):
        """If user_roles is None, role-targeted notifications are excluded."""
        d = AppNotificationDispatcher()
        d.send("app-1", "App", "org-1", "Admin alert", "Details",
               target_type=TargetType.ROLE, target_value="admin")
        notifs = d.get_for_user("user-1", "org-1", user_roles=None)
        assert len(notifs) == 0


class TestQuery:
    def test_get_by_app(self):
        d = AppNotificationDispatcher()
        d.send("app-1", "App1", "org-1", "A", "B")
        d.send("app-2", "App2", "org-1", "C", "D")
        d.send("app-1", "App1", "org-1", "E", "F")
        results = d.get_by_app("app-1")
        assert len(results) == 2

    def test_newest_first(self):
        d = AppNotificationDispatcher()
        d.send("app-1", "App", "org-1", "First", "B")
        d.send("app-1", "App", "org-1", "Second", "B")
        results = d.get_for_user("user-1", "org-1")
        assert results[0].title == "Second"

    def test_limit(self):
        d = AppNotificationDispatcher()
        for i in range(10):
            d.send("app-1", "App", "org-1", f"N{i}", "B")
        results = d.get_for_user("user-1", "org-1", limit=3)
        assert len(results) == 3
