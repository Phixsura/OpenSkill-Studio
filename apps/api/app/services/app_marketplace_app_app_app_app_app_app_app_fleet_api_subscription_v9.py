"""Fleet API Subscription v9 — track API subscription and webhook events."""
from __future__ import annotations
def fleet_api_subscription_v9(subs: list[dict]) -> dict:
    active = [s for s in subs if s.get("active")]
    events_delivered = sum(s.get("events_today", 0) for s in subs)
    failed = sum(s.get("failed_today", 0) for s in subs)
    return {"subscriptions": len(subs), "active": len(active), "events_today": events_delivered,
            "failed_today": failed, "healthy": failed == 0}
