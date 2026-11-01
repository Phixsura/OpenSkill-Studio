"""Endpoint lifecycle manager — manage endpoint creation, deprecation, sunset."""
from __future__ import annotations


class EndpointLifecycle:
    STATES = ("draft", "active", "deprecated", "sunset", "removed")

    def __init__(self):
        self._endpoints: dict[str, dict] = {}

    def create(self, path: str, version: str, owner: str) -> dict:
        self._endpoints[path] = {"path": path, "version": version, "owner": owner,
                                  "state": "draft", "consumers": 0}
        return self._endpoints[path]

    def activate(self, path: str) -> dict:
        self._endpoints[path]["state"] = "active"
        return {"path": path, "state": "active"}

    def deprecate(self, path: str, sunset_date: str, replacement: str = "") -> dict:
        ep = self._endpoints[path]
        ep["state"] = "deprecated"
        ep["sunset_date"] = sunset_date
        ep["replacement"] = replacement
        return ep

    def sunset(self, path: str) -> dict:
        self._endpoints[path]["state"] = "sunset"
        return {"path": path, "state": "sunset"}

    def remove(self, path: str) -> dict:
        self._endpoints[path]["state"] = "removed"
        return {"path": path, "state": "removed"}

    def by_state(self, state: str) -> list[dict]:
        return [e for e in self._endpoints.values() if e["state"] == state]

    def stats(self) -> dict:
        by_state = {}
        for e in self._endpoints.values():
            by_state[e["state"]] = by_state.get(e["state"], 0) + 1
        return {"total": len(self._endpoints), "by_state": by_state}
