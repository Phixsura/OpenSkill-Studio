"""Request deduplication — detect and filter duplicate requests."""
from __future__ import annotations
import hashlib
import time

_seen: dict[str, float] = {}


def fingerprint_request(method: str, path: str, body: str = "", user: str = "") -> str:
    payload = f"{method}:{path}:{body}:{user}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def is_duplicate(fingerprint: str, window_sec: int = 5) -> dict:
    now = time.time()
    last_seen = _seen.get(fingerprint)
    if last_seen and now - last_seen < window_sec:
        return {"duplicate": True, "age_sec": round(now - last_seen, 2)}
    _seen[fingerprint] = now
    return {"duplicate": False}


def dedup_stats() -> dict:
    now = time.time()
    active = sum(1 for ts in _seen.values() if now - ts < 60)
    return {"total_tracked": len(_seen), "active_window": active}


def clear_seen() -> None:
    _seen.clear()
