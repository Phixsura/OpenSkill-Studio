"""Fleet AI Competitive v7 — track AI platform competitive intelligence."""
from __future__ import annotations
def fleet_ai_competitive_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    competitors = sum(t.get("competitors", 0) for t in trackers)
    win_rate = round(sum(t.get("win_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    market_share = round(sum(t.get("share_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    features_ahead = sum(t.get("ahead", 0) for t in trackers)
    return {"trackers": len(trackers), "active": len(active), "competitors": competitors,
            "win_rate": win_rate, "share": market_share, "ahead": features_ahead, "leading": win_rate > 60}
