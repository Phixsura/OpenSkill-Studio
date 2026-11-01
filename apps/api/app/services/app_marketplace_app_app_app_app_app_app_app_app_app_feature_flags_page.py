"""Feature flags page — manage feature flags with rollout controls."""

import html
import hashlib


def build_feature_flags_page(*, flags: list[dict]) -> dict:
    items = []
    enabled = 0
    for f in flags:
        is_enabled = f.get("enabled", False)
        if is_enabled:
            enabled += 1
        items.append({
            "key": f.get("key", ""),
            "description": html.escape(f.get("description", "")),
            "enabled": is_enabled,
            "rollout_pct": f.get("rollout_pct", 100),
            "environment": f.get("environment", "all"),
            "created_by": html.escape(f.get("created_by", "")),
        })
    return {"flags": items, "total": len(items), "enabled": enabled,
            "disabled": len(items) - enabled}


def evaluate_flag(*, flag_key: str, user_id: str, rollout_pct: int = 100,
                    enabled: bool = True) -> dict:
    if not enabled:
        return {"enabled": False, "reason": "flag_disabled"}
    if rollout_pct >= 100:
        return {"enabled": True, "reason": "full_rollout"}
    bucket = int(hashlib.sha256(f"{flag_key}:{user_id}".encode()).hexdigest()[:4], 16) % 100
    return {"enabled": bucket < rollout_pct, "bucket": bucket, "reason": "rollout"}
