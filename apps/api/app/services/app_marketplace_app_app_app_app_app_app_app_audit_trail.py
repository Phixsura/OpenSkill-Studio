"""Audit trail — immutable event log for compliance."""
from __future__ import annotations
import hashlib
import html
import time


_trail: list[dict] = []


def append_event(actor: str, action: str, resource: str, detail: str = "") -> dict:
    seq = len(_trail) + 1
    prev_hash = _trail[-1]["hash"] if _trail else "0" * 64
    payload = f"{seq}:{actor}:{action}:{resource}:{prev_hash}"
    entry = {
        "seq": seq,
        "timestamp": time.time(),
        "actor": html.escape(actor),
        "action": action,
        "resource": html.escape(resource),
        "detail": html.escape(detail),
        "hash": hashlib.sha256(payload.encode()).hexdigest(),
        "prev_hash": prev_hash,
    }
    _trail.append(entry)
    return entry


def get_trail(limit: int = 50) -> dict:
    items = list(reversed(_trail[-limit:]))
    return {"events": items, "total": len(_trail), "shown": len(items)}


def verify_chain() -> dict:
    for i, entry in enumerate(_trail):
        expected_prev = _trail[i - 1]["hash"] if i > 0 else "0" * 64
        if entry["prev_hash"] != expected_prev:
            return {"valid": False, "broken_at": entry["seq"]}
    return {"valid": True, "length": len(_trail)}


def reset_trail() -> None:
    _trail.clear()
