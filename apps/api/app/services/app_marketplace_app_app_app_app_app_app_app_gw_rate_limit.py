"""API gateway rate limiter — per-client rate limiting at the gateway."""
from __future__ import annotations
import time

_limits: dict[str, dict] = {}


def configure_limit(client_id: str, requests_per_min: int, burst: int = 0) -> dict:
    _limits[client_id] = {"client_id": client_id, "rpm": requests_per_min,
                            "burst": burst or requests_per_min, "current": 0,
                            "window_start": time.time(), "blocked": 0}
    return _limits[client_id]


def check_rate_limit(client_id: str) -> dict:
    limit = _limits.get(client_id)
    if not limit:
        return {"allowed": True, "reason": "no_limit_configured"}
    now = time.time()
    if now - limit["window_start"] >= 60:
        limit["current"] = 0
        limit["window_start"] = now
    if limit["current"] >= limit["burst"]:
        limit["blocked"] += 1
        return {"allowed": False, "remaining": 0, "limit": limit["rpm"],
                "retry_after_sec": round(60 - (now - limit["window_start"]))}
    limit["current"] += 1
    return {"allowed": True, "remaining": limit["burst"] - limit["current"],
            "limit": limit["rpm"]}


def rate_limit_stats() -> dict:
    total_blocked = sum(l["blocked"] for l in _limits.values())
    return {"configured_clients": len(_limits), "total_blocked": total_blocked}


def clear_limits() -> None:
    _limits.clear()
