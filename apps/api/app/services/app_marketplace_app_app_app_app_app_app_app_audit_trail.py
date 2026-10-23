"""Platform audit trail — immutable log of all administrative actions."""
from __future__ import annotations
import secrets
import time
import html


class AuditTrail:
    def __init__(self):
        self._events: list[dict] = []

    def log(self, *, actor: str, action: str, resource: str,
            details: str = "", ip: str = "", now: float | None = None) -> dict:
        ts = now if now is not None else time.time()
        event = {"id": f"aud_{secrets.token_hex(6)}", "actor": html.escape(actor),
                 "action": action, "resource": html.escape(resource),
                 "details": html.escape(details[:500]), "ip": ip, "timestamp": ts}
        self._events.append(event)
        return {"id": event["id"], "logged": True}

    def query(self, *, actor: str | None = None, action: str | None = None,
               resource: str | None = None, limit: int = 50) -> list[dict]:
        results = self._events
        if actor:
            results = [e for e in results if e["actor"] == actor]
        if action:
            results = [e for e in results if e["action"] == action]
        if resource:
            results = [e for e in results if resource in e["resource"]]
        return list(reversed(results[-limit:]))

    def stats(self) -> dict:
        by_action: dict[str, int] = {}
        by_actor: dict[str, int] = {}
        for e in self._events:
            by_action[e["action"]] = by_action.get(e["action"], 0) + 1
            by_actor[e["actor"]] = by_actor.get(e["actor"], 0) + 1
        return {"total_events": len(self._events), "by_action": by_action,
                "by_actor": by_actor, "unique_actors": len(by_actor)}
