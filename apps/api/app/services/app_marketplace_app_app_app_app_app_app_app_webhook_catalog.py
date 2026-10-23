"""Webhook event catalog — define, document, and validate webhook event types."""
from __future__ import annotations
import html


class WebhookEventCatalog:
    def __init__(self):
        self._events: dict[str, dict] = {}

    def register(self, event_type: str, *, description: str,
                  payload_schema: dict, category: str = "general") -> dict:
        self._events[event_type] = {
            "type": event_type, "description": html.escape(description),
            "schema": payload_schema, "category": category,
        }
        return {"registered": event_type, "category": category}

    def validate_payload(self, event_type: str, payload: dict) -> dict:
        event = self._events.get(event_type)
        if not event:
            return {"valid": False, "error": f"Unknown event type: {event_type}"}
        required = event["schema"].get("required", [])
        missing = [f for f in required if f not in payload]
        if missing:
            return {"valid": False, "missing_fields": missing}
        return {"valid": True, "event_type": event_type}

    def list_events(self, *, category: str | None = None) -> list[dict]:
        events = list(self._events.values())
        if category:
            events = [e for e in events if e["category"] == category]
        return [{"type": e["type"], "description": e["description"],
                 "category": e["category"], "fields": list(e["schema"].get("required", []))}
                for e in events]

    def categories(self) -> list[str]:
        return sorted({e["category"] for e in self._events.values()})
