"""Fleet AI Platform Value v7 — track AI platform value creation."""
from __future__ import annotations
def fleet_ai_platform_value_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    total_value = round(sum(t.get("value_usd", 0) for t in trackers), 2)
    roi = round(sum(t.get("roi_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    time_saved_h = sum(t.get("hours_saved", 0) for t in trackers)
    return {"trackers": len(trackers), "active": len(active), "value_usd": total_value,
            "roi": roi, "hours_saved": time_saved_h, "valuable": roi > 200}
