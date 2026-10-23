"""Webhook filter — filter webhook events by type, source, and conditions."""
from __future__ import annotations


def create_filter(*, event_types: list[str] | None = None,
                    sources: list[str] | None = None,
                    conditions: dict | None = None) -> dict:
    return {"event_types": event_types or [], "sources": sources or [],
            "conditions": conditions or {}, "active": True}


def apply_filter(events: list[dict], webhook_filter: dict) -> list[dict]:
    result = events
    types = webhook_filter.get("event_types", [])
    sources = webhook_filter.get("sources", [])
    conditions = webhook_filter.get("conditions", {})
    if types:
        result = [e for e in result if e.get("type") in types]
    if sources:
        result = [e for e in result if e.get("source") in sources]
    for key, value in conditions.items():
        result = [e for e in result if e.get("payload", {}).get(key) == value]
    return result


def filter_stats(original: int, filtered: int) -> dict:
    dropped = original - filtered
    return {"original": original, "filtered": filtered, "dropped": dropped,
            "drop_rate": round(dropped / max(original, 1) * 100, 1)}
