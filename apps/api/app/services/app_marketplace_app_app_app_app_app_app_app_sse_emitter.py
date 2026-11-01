"""SSE event emitter — server-sent events for real-time updates."""
from __future__ import annotations
import time

_channels: dict[str, list[dict]] = {}


def emit_event(channel: str, event_type: str, data: dict) -> dict:
    event = {"type": event_type, "data": data, "id": len(_channels.get(channel, [])) + 1,
             "timestamp": time.time()}
    _channels.setdefault(channel, []).append(event)
    return event


def get_events(channel: str, since_id: int = 0) -> dict:
    events = _channels.get(channel, [])
    new_events = [e for e in events if e["id"] > since_id]
    return {"channel": channel, "events": new_events, "count": len(new_events),
            "latest_id": events[-1]["id"] if events else 0}


def channel_stats() -> dict:
    total_events = sum(len(evts) for evts in _channels.values())
    return {"total_channels": len(_channels), "total_events": total_events,
            "channels": list(_channels.keys())}


def clear_channels() -> None:
    _channels.clear()
