"""Feature toggle router — route requests based on feature flags."""
from __future__ import annotations
import hashlib


def route_request(user_id: str, toggles: dict[str, dict]) -> dict:
    enabled = {}
    for flag, config in toggles.items():
        if not config.get("enabled", False):
            enabled[flag] = False
            continue
        rollout = config.get("rollout_pct", 100)
        if rollout >= 100:
            enabled[flag] = True
        else:
            h = int(hashlib.md5(f"{flag}:{user_id}".encode()).hexdigest(), 16) % 100
            enabled[flag] = h < rollout
    return {"user_id": user_id, "flags": enabled,
            "enabled_count": sum(1 for v in enabled.values() if v),
            "total_flags": len(enabled)}


def toggle_summary(toggles: dict[str, dict]) -> dict:
    active = sum(1 for t in toggles.values() if t.get("enabled"))
    full_rollout = sum(1 for t in toggles.values() if t.get("enabled") and t.get("rollout_pct", 100) >= 100)
    return {"total": len(toggles), "active": active, "inactive": len(toggles) - active,
            "full_rollout": full_rollout, "partial_rollout": active - full_rollout}
