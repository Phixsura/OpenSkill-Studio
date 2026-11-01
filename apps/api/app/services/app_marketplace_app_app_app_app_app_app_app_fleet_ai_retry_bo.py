"""Fleet AI Retry Backoff — track exponential backoff retry strategies."""
from __future__ import annotations
def fleet_ai_retry_backoff(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    retries_24h = sum(m.get("retries_24h", 0) for m in managers)
    max_backoff_s = max((m.get("max_backoff_s", 0) for m in managers), default=0)
    jitter_enabled = all(m.get("jitter", False) for m in managers)
    return {"managers": len(managers), "active": len(active), "retries_24h": retries_24h,
            "max_backoff_s": max_backoff_s, "jitter": jitter_enabled, "smart": jitter_enabled}
