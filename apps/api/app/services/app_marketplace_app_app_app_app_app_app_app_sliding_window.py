"""Sliding window rate limiter — track requests in sliding time windows."""
from __future__ import annotations
import time

_windows: dict[str, list[float]] = {}


def record_request(key: str, now: float | None = None) -> None:
    now = now or time.time()
    _windows.setdefault(key, []).append(now)


def check_rate(key: str, window_sec: int = 60, limit: int = 100, now: float | None = None) -> dict:
    now = now or time.time()
    requests = _windows.get(key, [])
    # Clean old entries
    recent = [t for t in requests if now - t < window_sec]
    _windows[key] = recent
    count = len(recent)
    allowed = count < limit
    return {"key": key, "count": count, "limit": limit, "window_sec": window_sec,
            "allowed": allowed, "remaining": max(0, limit - count),
            "retry_after": 0 if allowed else 1}


def window_stats() -> dict:
    return {"total_keys": len(_windows),
            "total_requests": sum(len(v) for v in _windows.values())}


def clear_windows() -> None:
    _windows.clear()
