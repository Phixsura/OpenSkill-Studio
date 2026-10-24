"""Tooltip builder — contextual tooltips with positioning and rich content."""
from __future__ import annotations
import html


TOOLTIP_PRESETS = {
    "api_key": {"title": "API Key", "body": "Use this key to authenticate your API requests. Keep it secret.", "position": "bottom"},
    "webhook_url": {"title": "Webhook URL", "body": "We'll send event notifications to this endpoint.", "position": "right"},
    "rate_limit": {"title": "Rate Limit", "body": "Maximum number of requests per minute for this plan.", "position": "top"},
    "deploy": {"title": "Deploy", "body": "Push your latest changes to the selected environment.", "position": "bottom"},
    "sandbox": {"title": "Sandbox Mode", "body": "Test your integration without affecting production data.", "position": "right"},
}


def get_tooltip(key: str) -> dict:
    preset = TOOLTIP_PRESETS.get(key)
    if not preset:
        return {"error": f"Unknown tooltip: {key}"}
    return {"key": key, "title": html.escape(preset["title"]),
            "body": html.escape(preset["body"]), "position": preset["position"]}


def create_tooltip(*, title: str, body: str, position: str = "top") -> dict:
    if position not in ("top", "bottom", "left", "right"):
        position = "top"
    return {"title": html.escape(title), "body": html.escape(body[:200]), "position": position}


def list_tooltips() -> list[str]:
    return sorted(TOOLTIP_PRESETS.keys())
