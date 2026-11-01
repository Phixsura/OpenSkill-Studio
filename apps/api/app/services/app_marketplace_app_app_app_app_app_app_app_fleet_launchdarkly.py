"""Fleet LaunchDarkly — track feature flag management."""
from __future__ import annotations
def fleet_launchdarkly_status(flags: list[dict]) -> dict:
    active = [f for f in flags if f.get("active", True)]
    stale = [f for f in flags if f.get("age_days", 0) > 90]
    targeting = [f for f in active if f.get("targeting_on", False)]
    return {"total": len(flags), "active": len(active), "stale": len(stale),
            "targeting": len(targeting), "needs_cleanup": len(stale) > 10}
