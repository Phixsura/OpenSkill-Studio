"""Rate limit policy — define and check rate limiting rules."""
from __future__ import annotations
import time

_buckets: dict[str, dict] = {}


def define_policy(name: str, requests_per_min: int, burst: int = 0) -> dict:
    return {"name": name, "requests_per_min": requests_per_min,
            "burst": burst or requests_per_min, "window_sec": 60}


def check_rate(policy: dict, client_id: str) -> dict:
    key = f"{policy['name']}:{client_id}"
    now = time.time()
    bucket = _buckets.get(key)
    if not bucket or now - bucket["window_start"] >= policy["window_sec"]:
        _buckets[key] = {"count": 1, "window_start": now}
        return {"allowed": True, "remaining": policy["requests_per_min"] - 1,
                "limit": policy["requests_per_min"], "retry_after": 0}
    bucket["count"] += 1
    if bucket["count"] > policy["burst"]:
        retry_after = round(policy["window_sec"] - (now - bucket["window_start"]))
        return {"allowed": False, "remaining": 0, "limit": policy["requests_per_min"],
                "retry_after": max(1, retry_after)}
    remaining = max(0, policy["requests_per_min"] - bucket["count"])
    return {"allowed": True, "remaining": remaining,
            "limit": policy["requests_per_min"], "retry_after": 0}


def reset_buckets() -> None:
    _buckets.clear()
