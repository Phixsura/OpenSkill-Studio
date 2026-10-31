"""Fleet Webhook Filter v9 — track webhook event filtering rules."""
from __future__ import annotations
def fleet_webhook_filter_v9(filters: list[dict]) -> dict:
    active = [f for f in filters if f.get("active")]
    events_filtered = sum(f.get("filtered_today", 0) for f in filters)
    events_passed = sum(f.get("passed_today", 0) for f in filters)
    return {"filters": len(filters), "active": len(active), "filtered_today": events_filtered,
            "passed_today": events_passed, "healthy": True}
