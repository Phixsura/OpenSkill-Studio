"""Webhook event catalog — define and document webhook events."""
from __future__ import annotations
import html


EVENTS = {
    "app.installed": {"category": "lifecycle", "description": "App installed by a user"},
    "app.uninstalled": {"category": "lifecycle", "description": "App uninstalled"},
    "app.updated": {"category": "lifecycle", "description": "App configuration updated"},
    "user.created": {"category": "user", "description": "New user created"},
    "user.deleted": {"category": "user", "description": "User account deleted"},
    "payment.completed": {"category": "billing", "description": "Payment processed"},
    "payment.failed": {"category": "billing", "description": "Payment failed"},
    "deploy.started": {"category": "deploy", "description": "Deployment started"},
    "deploy.completed": {"category": "deploy", "description": "Deployment completed"},
    "deploy.failed": {"category": "deploy", "description": "Deployment failed"},
}


def list_events(category: str | None = None) -> dict:
    items = []
    for event_type, info in EVENTS.items():
        if category and info["category"] != category:
            continue
        items.append({"type": event_type, **info})
    categories = sorted({e["category"] for e in items})
    return {"events": items, "total": len(items), "categories": categories}


def validate_subscription(event_types: list[str]) -> dict:
    valid = [e for e in event_types if e in EVENTS]
    invalid = [e for e in event_types if e not in EVENTS]
    return {"valid": valid, "invalid": invalid, "valid_count": len(valid),
            "all_valid": len(invalid) == 0}
