"""Notification composer — build rich notifications for different channels."""
from __future__ import annotations
import html

TEMPLATES = {
    "app_installed": {"title": "New Install!", "icon": "📥", "priority": "normal"},
    "review_received": {"title": "New Review", "icon": "⭐", "priority": "normal"},
    "deploy_complete": {"title": "Deploy Complete", "icon": "🚀", "priority": "high"},
    "error_spike": {"title": "Error Spike", "icon": "🚨", "priority": "critical"},
    "plan_upgrade": {"title": "Plan Upgraded", "icon": "⬆️", "priority": "normal"},
    "milestone_reached": {"title": "Milestone!", "icon": "🏆", "priority": "normal"},
}


def compose_notification(event_type: str, *, data: dict) -> dict:
    template = TEMPLATES.get(event_type, {"title": event_type, "icon": "📌", "priority": "normal"})
    body = html.escape(data.get("message", ""))
    return {
        "title": template["title"], "body": body,
        "icon": template["icon"], "priority": template["priority"],
        "event_type": event_type,
        "action_url": data.get("url", ""),
        "channels": _pick_channels(template["priority"]),
    }


def _pick_channels(priority: str) -> list[str]:
    if priority == "critical":
        return ["in_app", "email", "slack", "sms"]
    if priority == "high":
        return ["in_app", "email", "slack"]
    return ["in_app", "email"]
