"""Notification Hub — centralized notification routing for the platform.

Routes notifications across channels (in-app, email, webhook, push)
with user preferences, dedup, batching, and delivery tracking.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class Channel(str, Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"
    PUSH = "push"


@dataclass
class NotificationTemplate:
    template_id: str
    event_type: str
    title_template: str
    body_template: str
    default_channels: list[Channel] = field(default_factory=list)


@dataclass
class SentNotification:
    notification_id: str
    event_type: str
    recipient: str
    channels: list[str]
    title: str
    body: str
    read: bool = False
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


class NotificationHubService:
    """Centralized notification routing with templates and preferences."""

    def __init__(self):
        self._templates: dict[str, NotificationTemplate] = {}
        self._preferences: dict[str, dict[str, list[Channel]]] = defaultdict(dict)
        self._sent: list[SentNotification] = []
        self._dedup_keys: set[str] = set()

    def register_template(self, event_type: str, title: str, body: str,
                          channels: list[Channel] | None = None) -> NotificationTemplate:
        tpl = NotificationTemplate(
            template_id=f"tpl_{secrets.token_urlsafe(6)}",
            event_type=event_type, title_template=title,
            body_template=body, default_channels=channels or [Channel.IN_APP],
        )
        self._templates[event_type] = tpl
        return tpl

    def set_preferences(self, user_id: str, event_type: str,
                        channels: list[Channel]) -> None:
        self._preferences[user_id][event_type] = channels

    def send(self, event_type: str, recipient: str, data: dict,
             dedup_key: str = "") -> SentNotification | None:
        if dedup_key and dedup_key in self._dedup_keys:
            return None
        if dedup_key:
            self._dedup_keys.add(dedup_key)

        tpl = self._templates.get(event_type)
        if not tpl:
            return None

        title = tpl.title_template
        body = tpl.body_template
        for k, v in data.items():
            title = title.replace(f"{{{{{k}}}}}", str(v))
            body = body.replace(f"{{{{{k}}}}}", str(v))

        channels = self._preferences.get(recipient, {}).get(
            event_type, tpl.default_channels)

        notification = SentNotification(
            notification_id=f"not_{secrets.token_urlsafe(8)}",
            event_type=event_type, recipient=recipient,
            channels=[c.value for c in channels],
            title=title, body=body,
        )
        self._sent.append(notification)
        return notification

    def get_inbox(self, user_id: str, unread_only: bool = False) -> list[SentNotification]:
        inbox = [n for n in self._sent if n.recipient == user_id]
        if unread_only:
            inbox = [n for n in inbox if not n.read]
        return inbox

    def mark_read(self, notification_id: str) -> bool:
        for n in self._sent:
            if n.notification_id == notification_id:
                n.read = True
                return True
        return False

    def get_unread_count(self, user_id: str) -> int:
        return sum(1 for n in self._sent if n.recipient == user_id and not n.read)
