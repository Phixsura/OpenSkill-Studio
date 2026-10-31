"""Notification Service — multi-channel notifications for developer platform events.

Sends notifications to extension developers about installs, reviews,
security alerts, billing events, and lifecycle changes via multiple channels.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class NotificationChannel(str, Enum):
    EMAIL = "email"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    SLACK = "slack"


class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class Notification:
    notification_id: str
    recipient_id: str
    channel: NotificationChannel
    priority: NotificationPriority
    title: str
    body: str
    metadata: dict = field(default_factory=dict)
    sent_at: str = ""
    read: bool = False


class NotificationService:
    """Multi-channel notification delivery and management."""

    def __init__(self):
        self._notifications: list[Notification] = []
        self._preferences: dict[str, dict[str, bool]] = {}  # user -> {channel: enabled}

    def set_preferences(self, user_id: str, preferences: dict[str, bool]) -> None:
        """Set notification channel preferences for a user."""
        self._preferences[user_id] = preferences

    def get_preferences(self, user_id: str) -> dict[str, bool]:
        return self._preferences.get(user_id, {c.value: True for c in NotificationChannel})

    def send(
        self, notification_id: str, recipient_id: str, title: str, body: str,
        channel: NotificationChannel = NotificationChannel.IN_APP,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        metadata: dict | None = None,
    ) -> Notification | None:
        """Send a notification if channel is enabled for recipient."""
        prefs = self.get_preferences(recipient_id)
        if not prefs.get(channel.value, True):
            return None  # Channel disabled by user

        notif = Notification(
            notification_id=notification_id, recipient_id=recipient_id,
            channel=channel, priority=priority,
            title=title, body=body, metadata=metadata or {},
            sent_at=datetime.now(timezone.utc).isoformat(),
        )
        self._notifications.append(notif)
        return notif

    def broadcast(
        self, recipient_ids: list[str], title: str, body: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
    ) -> int:
        """Send in-app notification to multiple recipients."""
        sent = 0
        for i, uid in enumerate(recipient_ids):
            result = self.send(f"broadcast-{i}", uid, title, body, priority=priority)
            if result:
                sent += 1
        return sent

    def get_inbox(self, user_id: str, unread_only: bool = False) -> list[Notification]:
        """Get notifications for a user."""
        notifs = [n for n in self._notifications if n.recipient_id == user_id]
        if unread_only:
            notifs = [n for n in notifs if not n.read]
        return sorted(notifs, key=lambda n: n.sent_at, reverse=True)

    def mark_read(self, notification_id: str) -> bool:
        for n in self._notifications:
            if n.notification_id == notification_id:
                n.read = True
                return True
        return False

    def unread_count(self, user_id: str) -> int:
        return sum(1 for n in self._notifications
                   if n.recipient_id == user_id and not n.read)
