"""Fleet feature flag analytics — track flag evaluation metrics."""
from __future__ import annotations
def fleet_ff_analytics(flags: list[dict]) -> dict:
    total_evals = sum(f.get("evaluations_24h", 0) for f in flags)
    enabled = [f for f in flags if f.get("enabled", False)]
    stale = [f for f in flags if f.get("age_days", 0) > 30 and f.get("enabled")]
    return {"total_flags": len(flags), "enabled": len(enabled), "total_evals": total_evals,
            "stale": len(stale), "cleanup_needed": len(stale) > 5}
