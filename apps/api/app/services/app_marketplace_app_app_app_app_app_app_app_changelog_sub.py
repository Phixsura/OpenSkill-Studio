"""Changelog subscriber — manage user subscriptions to changelogs."""
from __future__ import annotations
import time

_subs: dict[str, dict] = {}


def subscribe(user_id: str, channel: str = "email", frequency: str = "weekly") -> dict:
    valid_freq = {"immediate", "daily", "weekly"}
    valid_ch = {"email", "slack", "in_app"}
    if frequency not in valid_freq:
        return {"subscribed": False, "error": "invalid_frequency"}
    if channel not in valid_ch:
        return {"subscribed": False, "error": "invalid_channel"}
    _subs[user_id] = {"user_id": user_id, "channel": channel, "frequency": frequency,
                       "subscribed_at": time.time(), "active": True}
    return {"subscribed": True, "user_id": user_id, "channel": channel}


def unsubscribe(user_id: str) -> dict:
    if user_id not in _subs:
        return {"unsubscribed": False, "error": "not_found"}
    _subs[user_id]["active"] = False
    return {"unsubscribed": True}


def subscriber_stats() -> dict:
    active = sum(1 for s in _subs.values() if s["active"])
    by_channel: dict[str, int] = {}
    for s in _subs.values():
        if s["active"]:
            by_channel[s["channel"]] = by_channel.get(s["channel"], 0) + 1
    return {"total": len(_subs), "active": active, "by_channel": by_channel}


def clear_subs() -> None:
    _subs.clear()
