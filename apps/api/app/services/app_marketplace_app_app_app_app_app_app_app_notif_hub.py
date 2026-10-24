"""Platform notification hub — multi-channel notification delivery."""
from __future__ import annotations
from collections import defaultdict


class NotificationHub:
    def __init__(self):
        self._channels = {"email", "slack", "webhook", "sms", "push"}
        self._sent: list[dict] = []
        self._preferences: dict[str, set[str]] = {}

    def set_preferences(self, user_id: str, channels: list[str]) -> dict:
        valid = set(channels) & self._channels
        self._preferences[user_id] = valid
        return {"user_id": user_id, "channels": sorted(valid)}

    def send(self, user_id: str, title: str, body: str, priority: str = "normal") -> dict:
        channels = self._preferences.get(user_id, {"email"})
        deliveries = []
        for ch in sorted(channels):
            entry = {"user_id": user_id, "channel": ch, "title": title,
                     "priority": priority, "status": "delivered"}
            self._sent.append(entry)
            deliveries.append(entry)
        return {"delivered_to": len(deliveries), "channels": sorted(channels)}

    def stats(self) -> dict:
        by_channel: dict[str, int] = defaultdict(int)
        for s in self._sent:
            by_channel[s["channel"]] += 1
        return {"total_sent": len(self._sent), "by_channel": dict(by_channel),
                "users_with_prefs": len(self._preferences)}
