"""Event log formatter — format event log entries for display."""

from datetime import UTC, datetime


def format_event_log_entry(event: dict) -> dict:
    """Format an event for display in the developer dashboard."""
    return {
        "event_id": event.get("event_id", ""),
        "event_type": event.get("event_type", ""),
        "status": "delivered" if event.get("delivered") else "pending",
        "timestamp": event.get("timestamp", datetime.now(UTC).isoformat()),
        "org_id": event.get("org_id", ""),
        "display": f"{event.get('event_type', '?')} → {event.get('org_id', '?')[:8]}",
    }


def format_event_log(events: list[dict]) -> list[dict]:
    return [format_event_log_entry(e) for e in events]


def summarize_event_log(events: list[dict]) -> dict:
    types = {}
    for e in events:
        t = e.get("event_type", "unknown")
        types[t] = types.get(t, 0) + 1
    return {"total": len(events), "by_type": types, "unique_types": len(types)}
