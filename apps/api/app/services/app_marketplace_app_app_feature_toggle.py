"""Feature toggle — user-level feature toggle with overrides."""

import hashlib


def evaluate_toggle(*, feature: str, user_id: str, default: bool = False,
                      overrides: dict[str, bool] | None = None,
                      rollout_pct: int = 100) -> dict:
    if overrides and user_id in overrides:
        return {"feature": feature, "enabled": overrides[user_id], "reason": "override"}
    if rollout_pct >= 100:
        return {"feature": feature, "enabled": True, "reason": "full_rollout"}
    if rollout_pct <= 0:
        return {"feature": feature, "enabled": default, "reason": "disabled"}
    bucket = int(hashlib.sha256(f"{feature}:{user_id}".encode()).hexdigest()[:4], 16) % 100
    enabled = bucket < rollout_pct
    return {"feature": feature, "enabled": enabled, "bucket": bucket, "reason": "rollout"}


def bulk_evaluate(*, features: list[dict], user_id: str) -> dict:
    results = {}
    for f in features:
        r = evaluate_toggle(feature=f["name"], user_id=user_id,
                             default=f.get("default", False),
                             rollout_pct=f.get("rollout_pct", 100))
        results[f["name"]] = r["enabled"]
    enabled_count = sum(1 for v in results.values() if v)
    return {"toggles": results, "total": len(results), "enabled": enabled_count}
