"""Fleet AI Market v7 — track AI platform market position."""
from __future__ import annotations
def fleet_ai_market_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    market_share = round(sum(t.get("share_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    tam = round(sum(t.get("tam_usd", 0) for t in trackers), 2)
    competitors = sum(t.get("competitors", 0) for t in trackers)
    win_rate = round(sum(t.get("win_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "share": market_share,
            "tam": tam, "competitors": competitors, "win_rate": win_rate, "leading": market_share > 20}
