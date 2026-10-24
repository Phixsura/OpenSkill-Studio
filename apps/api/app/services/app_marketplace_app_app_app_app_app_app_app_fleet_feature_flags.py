"""Fleet feature flags — track flag adoption and staleness."""
from __future__ import annotations
def fleet_feature_flags(flags: list[dict]) -> dict:
    enabled = [f for f in flags if f.get("enabled", False)]
    stale = [f for f in flags if f.get("age_days", 0) > 90]
    return {"total": len(flags), "enabled": len(enabled), "disabled": len(flags) - len(enabled),
            "stale": len(stale), "needs_cleanup": len(stale) > 0}
