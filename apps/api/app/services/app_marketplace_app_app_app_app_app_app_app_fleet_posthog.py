"""Fleet PostHog — track open-source product analytics."""
from __future__ import annotations
def fleet_posthog_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    events_24h = sum(i.get("events_24h", 0) for i in instances)
    feature_flags = sum(i.get("feature_flags", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "events_24h": events_24h,
            "feature_flags": feature_flags, "all_running": len(running) == len(instances)}
