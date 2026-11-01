"""Consumer Activity Feed — chronological activity stream with filtering."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()

ACTIVITY_TYPES = ("api_call", "key_created", "key_revoked", "config_changed",
                  "member_added", "member_removed", "plan_changed", "alert_triggered")


@dataclass
class Activity:
    activity_id: str
    consumer_id: str
    activity_type: str
    actor_id: str
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict = field(default_factory=dict)
    read: bool = False


@dataclass
class ActivityFeed:
    """Chronological activity feed with filtering and pagination."""

    _activities: list[Activity] = field(default_factory=list)
    _max_size: int = 10000

    def post(self, activity: Activity) -> dict:
        if activity.activity_type not in ACTIVITY_TYPES:
            raise ValueError(f"Invalid type: {activity.activity_type}")
        if len(self._activities) >= self._max_size:
            self._activities = self._activities[-(self._max_size // 2):]
        self._activities.append(activity)
        logger.info("activity_posted", activity_id=activity.activity_id,
                     type=activity.activity_type)
        return {"activity_id": activity.activity_id, "posted": True}

    def get_feed(self, consumer_id: str | None = None,
                 activity_type: str | None = None,
                 actor_id: str | None = None,
                 unread_only: bool = False,
                 limit: int = 50, offset: int = 0) -> list[dict]:
        filtered = self._activities
        if consumer_id:
            filtered = [a for a in filtered if a.consumer_id == consumer_id]
        if activity_type:
            filtered = [a for a in filtered if a.activity_type == activity_type]
        if actor_id:
            filtered = [a for a in filtered if a.actor_id == actor_id]
        if unread_only:
            filtered = [a for a in filtered if not a.read]
        # Reverse chronological
        filtered = list(reversed(filtered))
        page = filtered[offset:offset + limit]
        return [
            {"activity_id": a.activity_id, "type": a.activity_type,
             "actor": a.actor_id, "description": a.description,
             "timestamp": a.timestamp, "read": a.read}
            for a in page
        ]

    def mark_read(self, activity_id: str) -> dict:
        for a in self._activities:
            if a.activity_id == activity_id:
                a.read = True
                return {"marked": True}
        return {"marked": False}

    def mark_all_read(self, consumer_id: str) -> dict:
        count = 0
        for a in self._activities:
            if a.consumer_id == consumer_id and not a.read:
                a.read = True
                count += 1
        return {"marked": count}

    def get_unread_count(self, consumer_id: str) -> dict:
        count = sum(1 for a in self._activities
                    if a.consumer_id == consumer_id and not a.read)
        return {"consumer_id": consumer_id, "unread": count}

    def get_stats(self, consumer_id: str | None = None) -> dict:
        activities = self._activities
        if consumer_id:
            activities = [a for a in activities if a.consumer_id == consumer_id]
        by_type: dict[str, int] = {}
        for a in activities:
            by_type[a.activity_type] = by_type.get(a.activity_type, 0) + 1
        return {
            "total": len(activities),
            "unread": sum(1 for a in activities if not a.read),
            "by_type": by_type,
        }

    def delete_old(self, before_timestamp: str) -> dict:
        before = len(self._activities)
        self._activities = [a for a in self._activities if a.timestamp >= before_timestamp]
        return {"deleted": before - len(self._activities)}
