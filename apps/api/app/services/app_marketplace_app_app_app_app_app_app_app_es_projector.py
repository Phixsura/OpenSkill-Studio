"""Event sourcing projector — project events into read models."""
from __future__ import annotations
from collections import defaultdict


class EventProjector:
    def __init__(self):
        self._projections: dict[str, dict] = {}
        self._event_count = 0

    def register_projection(self, name: str, initial_state: dict | None = None) -> dict:
        self._projections[name] = {"name": name, "state": dict(initial_state or {}),
                                    "events_applied": 0}
        return self._projections[name]

    def apply(self, projection: str, event: dict, reducer: callable) -> dict:
        p = self._projections[projection]
        p["state"] = reducer(p["state"], event)
        p["events_applied"] += 1
        self._event_count += 1
        return {"projection": projection, "events_applied": p["events_applied"]}

    def get_state(self, projection: str) -> dict:
        return dict(self._projections[projection]["state"])

    def stats(self) -> dict:
        return {"projections": len(self._projections), "total_events": self._event_count}
