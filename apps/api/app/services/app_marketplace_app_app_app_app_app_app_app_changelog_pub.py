"""Changelog publisher — publish changelogs to multiple channels."""
from __future__ import annotations
import html
import time


CHANNELS = {"email", "slack", "in_app", "rss", "status_page"}


def publish_changelog(version: str, summary: str, changes: list[str],
                       channels: list[str]) -> dict:
    invalid = [c for c in channels if c not in CHANNELS]
    if invalid:
        return {"published": False, "error": f"invalid channels: {invalid}"}
    results = []
    for ch in channels:
        results.append({"channel": ch, "status": "delivered",
                         "version": version})
    return {"published": True, "version": version,
            "summary": html.escape(summary), "change_count": len(changes),
            "channels_delivered": len(results), "results": results}


def schedule_publish(version: str, publish_at: float, channels: list[str]) -> dict:
    delay = max(0, publish_at - time.time())
    return {"scheduled": True, "version": version, "channels": channels,
            "publish_at": publish_at, "delay_sec": round(delay)}
