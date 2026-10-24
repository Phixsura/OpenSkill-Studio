"""Webhook event router — route webhook events to registered handlers."""
from __future__ import annotations
from collections import defaultdict


class WebhookEventRouter:
    def __init__(self):
        self._handlers: dict[str, list[str]] = defaultdict(list)
        self._delivered = 0

    def register(self, event_type: str, handler_url: str) -> dict:
        self._handlers[event_type].append(handler_url)
        return {"event_type": event_type, "handler": handler_url,
                "total_handlers": len(self._handlers[event_type])}

    def route(self, event_type: str, payload: dict) -> dict:
        handlers = self._handlers.get(event_type, [])
        self._delivered += len(handlers)
        return {"event_type": event_type, "delivered_to": len(handlers),
                "handlers": handlers}

    def unregister(self, event_type: str, handler_url: str) -> dict:
        self._handlers[event_type] = [h for h in self._handlers[event_type] if h != handler_url]
        return {"removed": True}

    def stats(self) -> dict:
        total_handlers = sum(len(h) for h in self._handlers.values())
        return {"event_types": len(self._handlers), "total_handlers": total_handlers,
                "total_delivered": self._delivered}
