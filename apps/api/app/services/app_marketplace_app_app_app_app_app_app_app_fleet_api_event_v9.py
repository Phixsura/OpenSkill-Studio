"""Fleet API Event v9 — track API event publishing and consumption."""
from __future__ import annotations
def fleet_api_event_v9(events: list[dict]) -> dict:
    published = sum(e.get("published_today", 0) for e in events)
    consumed = sum(e.get("consumed_today", 0) for e in events)
    failed = sum(e.get("failed", 0) for e in events)
    return {"event_types": len(events), "published_today": published,
            "consumed_today": consumed, "failed": failed, "healthy": failed == 0}
