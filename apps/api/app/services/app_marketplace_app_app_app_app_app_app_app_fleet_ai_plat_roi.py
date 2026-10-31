"""Fleet AI Platform ROI — track return on investment for AI platform."""
from __future__ import annotations
def fleet_ai_platform_roi(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    investment_usd = round(sum(t.get("investment", 0) for t in trackers), 2)
    returns_usd = round(sum(t.get("returns", 0) for t in trackers), 2)
    roi_pct = round((returns_usd - investment_usd) / max(investment_usd, 1) * 100, 1)
    return {"trackers": len(trackers), "active": len(active), "investment": investment_usd,
            "returns": returns_usd, "roi_pct": roi_pct, "profitable": roi_pct > 100}
