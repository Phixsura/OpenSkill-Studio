"""Webhook event filter — filter events before delivery to subscribers."""
from __future__ import annotations


class WebhookEventFilter:
    def __init__(self):
        self._filters: dict[str, dict] = {}

    def add_filter(self, subscriber_id: str, event_types: list[str],
                   include_fields: list[str] | None = None) -> dict:
        self._filters[subscriber_id] = {"event_types": set(event_types),
                                          "include_fields": include_fields}
        return {"subscriber": subscriber_id, "events": len(event_types)}

    def should_deliver(self, subscriber_id: str, event_type: str) -> dict:
        f = self._filters.get(subscriber_id)
        if not f:
            return {"deliver": True, "reason": "no_filter"}
        deliver = event_type in f["event_types"] or "*" in f["event_types"]
        return {"deliver": deliver, "subscriber": subscriber_id, "event": event_type}

    def filter_payload(self, subscriber_id: str, payload: dict) -> dict:
        f = self._filters.get(subscriber_id)
        if not f or not f["include_fields"]:
            return payload
        return {k: v for k, v in payload.items() if k in f["include_fields"]}

    def stats(self) -> dict:
        return {"subscribers_with_filters": len(self._filters)}
