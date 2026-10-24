"""Fleet Feature Flag v9 — track feature flag states and rollout percentages."""
from __future__ import annotations
def fleet_feature_flag_v9(flags: list[dict]) -> dict:
    enabled = [f for f in flags if f.get("enabled")]
    stale = [f for f in flags if f.get("days_since_change", 0) > 90]
    avg_rollout = sum(f.get("rollout_pct", 0) for f in flags) / len(flags) if flags else 0
    return {"total": len(flags), "enabled": len(enabled), "stale": len(stale),
            "avg_rollout_pct": round(avg_rollout, 1), "healthy": len(stale) == 0}
