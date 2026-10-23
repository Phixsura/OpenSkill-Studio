"""Notification preferences — per-channel, per-category settings."""
from __future__ import annotations

CHANNELS = ("email", "push", "slack", "in_app")
CATEGORIES = ("security", "billing", "deploy", "review", "mention", "marketing")


def default_prefs() -> dict:
    return {cat: {ch: cat != "marketing" for ch in CHANNELS} for cat in CATEGORIES}


def update_prefs(prefs: dict, *, category: str, channel: str, enabled: bool) -> dict:
    if category not in CATEGORIES:
        return {"error": f"Unknown category: {category}"}
    if channel not in CHANNELS:
        return {"error": f"Unknown channel: {channel}"}
    if category not in prefs:
        prefs[category] = {ch: True for ch in CHANNELS}
    prefs[category][channel] = enabled
    return {"status": "updated", "category": category, "channel": channel, "enabled": enabled}


def summarize_prefs(prefs: dict) -> dict:
    total = 0
    enabled = 0
    by_channel: dict[str, int] = {ch: 0 for ch in CHANNELS}
    muted_categories: list[str] = []
    for cat in CATEGORIES:
        cat_prefs = prefs.get(cat, {})
        cat_enabled = 0
        for ch in CHANNELS:
            total += 1
            if cat_prefs.get(ch, False):
                enabled += 1
                by_channel[ch] += 1
                cat_enabled += 1
        if cat_enabled == 0:
            muted_categories.append(cat)
    return {"total_settings": total, "enabled": enabled,
            "by_channel": by_channel, "muted_categories": muted_categories}
