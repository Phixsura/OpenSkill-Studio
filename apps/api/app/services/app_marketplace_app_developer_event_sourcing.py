"""Event sourcing — append-only event log for app state reconstruction."""

from datetime import datetime, timezone


def append_event(*, stream_id: str, event_type: str, data: dict, version: int) -> dict:
    return {"stream_id": stream_id, "event_type": event_type, "data": data,
            "version": version, "timestamp": datetime.now(timezone.utc).isoformat()}


def replay_events(*, events: list[dict]) -> dict:
    state: dict = {}
    for e in sorted(events, key=lambda x: x.get("version", 0)):
        if e["event_type"] == "created":
            state = {**e["data"]}
        elif e["event_type"] == "updated":
            state.update(e["data"])
        elif e["event_type"] == "deleted":
            state = {"_deleted": True, **state}
    return {"state": state, "version": events[-1]["version"] if events else 0, "event_count": len(events)}


def get_event_stream_info(*, events: list[dict]) -> dict:
    types = {}
    for e in events:
        t = e.get("event_type", "unknown")
        types[t] = types.get(t, 0) + 1
    return {"total_events": len(events), "event_types": types,
            "first_event": events[0]["timestamp"] if events else None,
            "last_event": events[-1]["timestamp"] if events else None}
