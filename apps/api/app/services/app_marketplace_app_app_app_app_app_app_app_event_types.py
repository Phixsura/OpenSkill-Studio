"""Webhook event type registry — catalog all available event types."""
from __future__ import annotations

EVENT_TYPES = {
    "app": [
        {"type": "app.installed", "description": "App installed by an organization", "category": "lifecycle"},
        {"type": "app.uninstalled", "description": "App removed from organization", "category": "lifecycle"},
        {"type": "app.updated", "description": "App version updated", "category": "lifecycle"},
        {"type": "app.suspended", "description": "App suspended for policy violation", "category": "lifecycle"},
    ],
    "user": [
        {"type": "user.created", "description": "New user registered", "category": "identity"},
        {"type": "user.deleted", "description": "User account deleted", "category": "identity"},
        {"type": "user.login", "description": "User logged in", "category": "auth"},
    ],
    "deploy": [
        {"type": "deploy.started", "description": "Deployment initiated", "category": "operations"},
        {"type": "deploy.completed", "description": "Deployment finished", "category": "operations"},
        {"type": "deploy.failed", "description": "Deployment failed", "category": "operations"},
    ],
    "billing": [
        {"type": "billing.payment.succeeded", "description": "Payment processed", "category": "finance"},
        {"type": "billing.payment.failed", "description": "Payment failed", "category": "finance"},
        {"type": "billing.subscription.changed", "description": "Plan changed", "category": "finance"},
    ],
}


def list_event_types(*, group: str | None = None) -> list[dict]:
    if group and group in EVENT_TYPES:
        return EVENT_TYPES[group]
    return [e for events in EVENT_TYPES.values() for e in events]


def list_groups() -> list[str]:
    return sorted(EVENT_TYPES.keys())


def search_event_types(query: str) -> list[dict]:
    q = query.lower()
    return [e for e in list_event_types() if q in e["type"] or q in e["description"].lower()]
