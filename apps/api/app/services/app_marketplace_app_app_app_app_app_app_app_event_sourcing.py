"""Event sourcing store — append-only event log with projections."""
from __future__ import annotations
import time

_events: list[dict] = []


def append_event(aggregate_id: str, event_type: str, data: dict) -> dict:
    seq = len(_events) + 1
    event = {"seq": seq, "aggregate_id": aggregate_id, "type": event_type,
             "data": data, "timestamp": time.time()}
    _events.append(event)
    return event


def get_events(aggregate_id: str, since_seq: int = 0) -> list[dict]:
    return [e for e in _events if e["aggregate_id"] == aggregate_id and e["seq"] > since_seq]


def project_state(aggregate_id: str) -> dict:
    events = get_events(aggregate_id)
    state: dict = {}
    for e in events:
        if e["type"] == "created":
            state = {**e["data"]}
        elif e["type"] == "updated":
            state.update(e["data"])
        elif e["type"] == "deleted":
            state["_deleted"] = True
    return {"aggregate_id": aggregate_id, "state": state, "version": len(events)}


def store_stats() -> dict:
    aggregates = len({e["aggregate_id"] for e in _events})
    by_type: dict[str, int] = {}
    for e in _events:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
    return {"total_events": len(_events), "aggregates": aggregates, "by_type": by_type}


def clear_events() -> None:
    _events.clear()
