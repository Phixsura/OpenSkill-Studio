"""Audit trail logger — immutable audit log for compliance."""
from __future__ import annotations
import hashlib, time


class AuditTrail:
    def __init__(self):
        self._entries: list[dict] = []

    def log(self, actor: str, action: str, resource: str, details: dict | None = None) -> dict:
        prev_hash = self._entries[-1]["hash"] if self._entries else "0" * 64
        entry = {"seq": len(self._entries) + 1, "timestamp": time.time(),
                 "actor": actor, "action": action, "resource": resource,
                 "details": details or {}, "prev_hash": prev_hash}
        raw = f"{entry['seq']}:{entry['actor']}:{entry['action']}:{entry['resource']}:{prev_hash}"
        entry["hash"] = hashlib.sha256(raw.encode()).hexdigest()
        self._entries.append(entry)
        return entry

    def verify_chain(self) -> dict:
        for i, entry in enumerate(self._entries):
            expected_prev = self._entries[i - 1]["hash"] if i > 0 else "0" * 64
            if entry["prev_hash"] != expected_prev:
                return {"valid": False, "broken_at": entry["seq"]}
        return {"valid": True, "entries": len(self._entries)}

    def query(self, actor: str = "", action: str = "", limit: int = 10) -> list[dict]:
        results = self._entries
        if actor:
            results = [e for e in results if e["actor"] == actor]
        if action:
            results = [e for e in results if e["action"] == action]
        return results[-limit:]
