"""Webhook Events — define and manage typed webhook event payloads.

Provides strongly-typed event definitions for all marketplace events,
with schema validation and payload construction helpers.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class EventCategory(str, Enum):
    EXTENSION = "extension"
    INSTALL = "install"
    REVIEW = "review"
    BILLING = "billing"
    SECURITY = "security"
    CONFIG = "config"


WEBHOOK_EVENT_TYPES = {
    "extension.published": {"category": EventCategory.EXTENSION, "description": "Extension version published"},
    "extension.deprecated": {"category": EventCategory.EXTENSION, "description": "Extension deprecated"},
    "extension.updated": {"category": EventCategory.EXTENSION, "description": "Extension metadata updated"},
    "install.created": {"category": EventCategory.INSTALL, "description": "Extension installed by an org"},
    "install.removed": {"category": EventCategory.INSTALL, "description": "Extension uninstalled"},
    "review.created": {"category": EventCategory.REVIEW, "description": "New review submitted"},
    "review.flagged": {"category": EventCategory.REVIEW, "description": "Review flagged for moderation"},
    "billing.subscribed": {"category": EventCategory.BILLING, "description": "New subscription created"},
    "billing.canceled": {"category": EventCategory.BILLING, "description": "Subscription canceled"},
    "billing.invoice": {"category": EventCategory.BILLING, "description": "Invoice generated"},
    "security.scan_completed": {"category": EventCategory.SECURITY, "description": "Security scan finished"},
    "security.vulnerability": {"category": EventCategory.SECURITY, "description": "Vulnerability detected"},
    "config.changed": {"category": EventCategory.CONFIG, "description": "Extension config changed"},
}


@dataclass
class WebhookEvent:
    event_id: str
    event_type: str
    timestamp: str
    extension_id: str
    payload: dict
    actor_id: str = ""
    org_id: str = ""


class WebhookEventBuilder:
    """Builds and validates webhook event payloads."""

    _counter = 0

    @classmethod
    def _next_id(cls) -> str:
        cls._counter += 1
        return f"evt_{cls._counter:08d}"

    @classmethod
    def build(cls, event_type: str, extension_id: str, payload: dict,
              actor_id: str = "", org_id: str = "") -> tuple[WebhookEvent | None, str]:
        """Build a validated webhook event."""
        if event_type not in WEBHOOK_EVENT_TYPES:
            return None, f"Unknown event type: {event_type}"
        event = WebhookEvent(
            event_id=cls._next_id(),
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            extension_id=extension_id,
            payload=payload,
            actor_id=actor_id,
            org_id=org_id,
        )
        return event, "OK"

    @staticmethod
    def list_event_types(category: EventCategory | None = None) -> list[dict]:
        """List available webhook event types."""
        events = []
        for name, info in WEBHOOK_EVENT_TYPES.items():
            if category and info["category"] != category:
                continue
            events.append({"name": name, "category": info["category"].value,
                           "description": info["description"]})
        return events

    @staticmethod
    def serialize(event: WebhookEvent) -> dict:
        """Serialize event to a JSON-safe dict for delivery."""
        return {
            "id": event.event_id,
            "type": event.event_type,
            "timestamp": event.timestamp,
            "extension_id": event.extension_id,
            "actor_id": event.actor_id,
            "org_id": event.org_id,
            "data": event.payload,
        }
