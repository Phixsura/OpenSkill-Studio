"""Feature flag — toggle features with rollout percentages."""

import hashlib


def evaluate_flag(*, flag_key: str, user_id: str, percentage: int = 100,
                   enabled: bool = True) -> dict:
    if not enabled:
        return {"flag": flag_key, "enabled": False, "reason": "flag_disabled"}
    if percentage >= 100:
        return {"flag": flag_key, "enabled": True, "reason": "full_rollout"}
    if percentage <= 0:
        return {"flag": flag_key, "enabled": False, "reason": "zero_rollout"}
    bucket = int(hashlib.sha256(f"{flag_key}:{user_id}".encode()).hexdigest()[:8], 16) % 100
    in_rollout = bucket < percentage
    return {"flag": flag_key, "enabled": in_rollout, "bucket": bucket,
            "reason": "in_rollout" if in_rollout else "out_of_rollout"}


def list_flags(*, flags: list[dict]) -> dict:
    return {"flags": [{"key": f["key"], "enabled": f.get("enabled", True),
                        "percentage": f.get("percentage", 100),
                        "description": f.get("description", "")} for f in flags],
            "total": len(flags),
            "active": sum(1 for f in flags if f.get("enabled", True))}
