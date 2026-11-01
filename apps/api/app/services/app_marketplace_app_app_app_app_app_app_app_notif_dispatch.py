"""Notification dispatcher — send notifications via multiple channels."""
from __future__ import annotations
import html
import time

_sent: list[dict] = []


def dispatch(recipient: str, channel: str, title: str, body: str, priority: str = "normal") -> dict:
    valid_channels = {"email", "push", "slack", "in_app", "sms"}
    if channel not in valid_channels:
        return {"sent": False, "error": "invalid_channel"}
    entry = {"recipient": recipient, "channel": channel,
             "title": html.escape(title), "body": html.escape(body),
             "priority": priority, "timestamp": time.time(), "status": "delivered"}
    _sent.append(entry)
    return {"sent": True, **entry}


def dispatch_multi(recipient: str, channels: list[str], title: str, body: str) -> dict:
    results = [dispatch(recipient, ch, title, body) for ch in channels]
    ok = sum(1 for r in results if r.get("sent"))
    return {"recipient": recipient, "channels_attempted": len(channels),
            "delivered": ok, "failed": len(channels) - ok}


def get_history(limit: int = 20) -> list[dict]:
    return list(reversed(_sent[-limit:]))


def clear_history() -> None:
    _sent.clear()
