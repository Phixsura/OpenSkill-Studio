"""Consumer API Changelog Subscriber — changelog subscription with notifications."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class ChangelogSubscriber:
    subscriber_id: str
    consumer_id: str
    email: str
    notify_breaking: bool = True
    notify_deprecation: bool = True
    notify_new_features: bool = True
    active: bool = True


@dataclass
class ChangeNotification:
    notification_id: str
    version: str
    change_type: str
    summary: str
    breaking: bool = False
    sent_to: list[str] = field(default_factory=list)


@dataclass
class ChangelogSubscriptionManager:
    """Manage changelog subscriptions and send notifications."""

    _subscribers: dict[str, ChangelogSubscriber] = field(default_factory=dict)
    _notifications: list[ChangeNotification] = field(default_factory=list)

    def subscribe(self, sub: ChangelogSubscriber) -> dict:
        if sub.subscriber_id in self._subscribers:
            raise ValueError(f"Subscriber {sub.subscriber_id} already exists")
        if not sub.email or "@" not in sub.email:
            raise ValueError("Valid email is required")
        self._subscribers[sub.subscriber_id] = sub
        logger.info("changelog_subscribed", subscriber_id=sub.subscriber_id)
        return {"subscriber_id": sub.subscriber_id, "email": sub.email}

    def unsubscribe(self, subscriber_id: str) -> dict:
        if subscriber_id in self._subscribers:
            del self._subscribers[subscriber_id]
            return {"unsubscribed": True}
        return {"unsubscribed": False}

    def update_preferences(self, subscriber_id: str, **kwargs) -> dict:
        sub = self._subscribers.get(subscriber_id)
        if not sub:
            raise ValueError(f"Subscriber {subscriber_id} not found")
        for key, value in kwargs.items():
            if hasattr(sub, key):
                setattr(sub, key, value)
        return {"subscriber_id": subscriber_id, "updated": True}

    def notify(self, version: str, change_type: str, summary: str,
               breaking: bool = False) -> dict:
        recipients = []
        for sub in self._subscribers.values():
            if not sub.active:
                continue
            if breaking and sub.notify_breaking:
                recipients.append(sub.email)
            elif change_type == "deprecated" and sub.notify_deprecation:
                recipients.append(sub.email)
            elif change_type in ("added", "changed") and sub.notify_new_features:
                recipients.append(sub.email)
            elif not breaking and change_type not in ("deprecated", "added", "changed"):
                recipients.append(sub.email)
        notification = ChangeNotification(
            notification_id=f"notif-{len(self._notifications)+1}",
            version=version, change_type=change_type,
            summary=summary, breaking=breaking, sent_to=recipients,
        )
        self._notifications.append(notification)
        logger.info("changelog_notified", version=version, recipients=len(recipients))
        return {"notification_id": notification.notification_id,
                "sent_to": len(recipients), "version": version}

    def get_subscriber(self, subscriber_id: str) -> dict | None:
        sub = self._subscribers.get(subscriber_id)
        if not sub:
            return None
        return {
            "subscriber_id": sub.subscriber_id, "email": sub.email,
            "active": sub.active, "notify_breaking": sub.notify_breaking,
            "notify_deprecation": sub.notify_deprecation,
            "notify_new_features": sub.notify_new_features,
        }

    def list_subscribers(self, consumer_id: str | None = None) -> list[dict]:
        subs = list(self._subscribers.values())
        if consumer_id:
            subs = [s for s in subs if s.consumer_id == consumer_id]
        return [{"subscriber_id": s.subscriber_id, "email": s.email,
                 "active": s.active} for s in subs]

    def get_notification_history(self, limit: int = 20) -> list[dict]:
        return [
            {"id": n.notification_id, "version": n.version,
             "type": n.change_type, "summary": n.summary,
             "sent_to": len(n.sent_to), "breaking": n.breaking}
            for n in self._notifications[-limit:]
        ]

    def get_stats(self) -> dict:
        subs = list(self._subscribers.values())
        return {
            "total_subscribers": len(subs),
            "active": sum(1 for s in subs if s.active),
            "total_notifications": len(self._notifications),
            "total_sent": sum(len(n.sent_to) for n in self._notifications),
        }
