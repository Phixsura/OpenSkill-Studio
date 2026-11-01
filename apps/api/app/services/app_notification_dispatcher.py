"""App Notification Dispatcher — send in-app notifications from installed apps to users.

Provides a structured notification channel for developer apps:
- App-scoped notifications (attributed to the sending app)
- Priority levels: info, warning, action_required
- Notification targeting: specific user, org role, all org members
- Read/unread tracking
- Bulk dismiss and mark-read
- Rate limiting per app (prevent notification spam)
- Notification history with pagination
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()


class NotificationPriority(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ACTION_REQUIRED = "action_required"


class TargetType(str, Enum):
    USER = "user"           # specific user_id
    ROLE = "role"           # all users with a role in the org
    ORG_ALL = "org_all"     # all org members


@dataclass
class AppNotification:
    """A notification sent by an installed app."""

    notification_id: str
    app_id: str
    app_name: str
    org_id: str
    title: str
    body: str
    priority: NotificationPriority
    target_type: TargetType
    target_value: str           # user_id, role name, or org_id
    action_url: str | None = None
    read: bool = False
    dismissed: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SendResult:
    """Result of sending a notification."""

    success: bool
    notification_id: str | None = None
    error: str | None = None
    recipients: int = 0


# Rate limit: max notifications per app per hour
RATE_LIMIT_PER_HOUR = 100
MAX_TITLE_LENGTH = 200
MAX_BODY_LENGTH = 2000


class AppNotificationDispatcher:
    """Dispatch and manage notifications from installed apps."""

    def __init__(self):
        # notification_id → AppNotification
        self._notifications: dict[str, AppNotification] = {}
        # (app_id, hour_key) → count
        self._rate_counts: dict[tuple[str, str], int] = defaultdict(int)
        self._next_id = 0

    # ── Send ─────────────────────────────────────────────

    def send(self, app_id: str, app_name: str, org_id: str,
             title: str, body: str,
             priority: NotificationPriority = NotificationPriority.INFO,
             target_type: TargetType = TargetType.ORG_ALL,
             target_value: str = "",
             action_url: str | None = None) -> SendResult:
        """Send a notification from an app."""
        # Validation
        if not title or len(title) > MAX_TITLE_LENGTH:
            return SendResult(success=False, error=f"Title must be 1-{MAX_TITLE_LENGTH} chars")
        if len(body) > MAX_BODY_LENGTH:
            return SendResult(success=False, error=f"Body exceeds {MAX_BODY_LENGTH} chars")
        if target_type == TargetType.USER and not target_value:
            return SendResult(success=False, error="target_value required for user targeting")

        # Rate limit
        hour_key = datetime.now(UTC).strftime("%Y-%m-%dT%H")
        rate_key = (app_id, hour_key)
        if self._rate_counts[rate_key] >= RATE_LIMIT_PER_HOUR:
            return SendResult(success=False,
                              error=f"Rate limit exceeded: {RATE_LIMIT_PER_HOUR}/hour")

        self._next_id += 1
        nid = f"notif-{self._next_id}"

        if not target_value:
            target_value = org_id

        notif = AppNotification(
            notification_id=nid,
            app_id=app_id, app_name=app_name, org_id=org_id,
            title=title, body=body, priority=priority,
            target_type=target_type, target_value=target_value,
            action_url=action_url,
        )
        self._notifications[nid] = notif
        self._rate_counts[rate_key] += 1

        log.info("notification.sent", notification_id=nid, app_id=app_id,
                 priority=priority.value, target=target_type.value)

        return SendResult(success=True, notification_id=nid, recipients=1)

    # ── Read/dismiss ─────────────────────────────────────

    def mark_read(self, notification_id: str, user_id: str, org_id: str) -> bool:
        """Mark a notification as read. Requires caller identity to prevent IDOR."""
        notif = self._notifications.get(notification_id)
        if notif is None or notif.org_id != org_id:
            return False
        if not self._targets_user(notif, user_id):
            return False
        notif.read = True
        return True

    def dismiss(self, notification_id: str, user_id: str, org_id: str) -> bool:
        """Dismiss a notification. Requires caller identity to prevent IDOR."""
        notif = self._notifications.get(notification_id)
        if notif is None or notif.org_id != org_id:
            return False
        if not self._targets_user(notif, user_id):
            return False
        notif.dismissed = True
        return True

    def mark_all_read(self, user_id: str, org_id: str,
                      user_roles: set[str] | None = None) -> int:
        """Mark all notifications targeting a user as read."""
        count = 0
        for notif in self._notifications.values():
            if notif.org_id != org_id or notif.dismissed:
                continue
            if self._targets_user(notif, user_id, user_roles):
                if not notif.read:
                    notif.read = True
                    count += 1
        return count

    def dismiss_all(self, user_id: str, org_id: str,
                    user_roles: set[str] | None = None) -> int:
        count = 0
        for notif in self._notifications.values():
            if notif.org_id != org_id:
                continue
            if self._targets_user(notif, user_id, user_roles) and not notif.dismissed:
                notif.dismissed = True
                count += 1
        return count

    # ── Query ────────────────────────────────────────────

    def get_for_user(self, user_id: str, org_id: str,
                     user_roles: set[str] | None = None,
                     unread_only: bool = False,
                     limit: int = 50) -> list[AppNotification]:
        """Get notifications visible to a user.

        user_roles: the user's roles in the org (e.g. {"admin", "instructor"}).
        Required for role-targeted notifications; if None, role-targeted
        notifications are excluded (fail-closed).
        """
        results = []
        for notif in self._notifications.values():
            if notif.org_id != org_id or notif.dismissed:
                continue
            if not self._targets_user(notif, user_id, user_roles):
                continue
            if unread_only and notif.read:
                continue
            results.append(notif)
        results.sort(key=lambda n: n.created_at, reverse=True)
        return results[:limit]

    def unread_count(self, user_id: str, org_id: str,
                     user_roles: set[str] | None = None) -> int:
        return len(self.get_for_user(user_id, org_id, user_roles=user_roles,
                                     unread_only=True, limit=10000))

    def get_by_app(self, app_id: str, limit: int = 50) -> list[AppNotification]:
        results = [n for n in self._notifications.values() if n.app_id == app_id]
        results.sort(key=lambda n: n.created_at, reverse=True)
        return results[:limit]

    def get_rate_usage(self, app_id: str) -> int:
        hour_key = datetime.now(UTC).strftime("%Y-%m-%dT%H")
        return self._rate_counts.get((app_id, hour_key), 0)

    # ── Internal ─────────────────────────────────────────

    @staticmethod
    def _targets_user(notif: AppNotification, user_id: str,
                      user_roles: set[str] | None = None) -> bool:
        """Check if a notification targets a user.

        Fail-closed for role targeting: if user_roles is None, role-targeted
        notifications are NOT shown (prevents leaking to unauthenticated callers).
        """
        if notif.target_type == TargetType.USER:
            return notif.target_value == user_id
        if notif.target_type == TargetType.ORG_ALL:
            return True  # caller already filtered by org_id
        if notif.target_type == TargetType.ROLE:
            # Fail-closed: no roles provided → deny
            if user_roles is None:
                return False
            return notif.target_value in user_roles
        return False
