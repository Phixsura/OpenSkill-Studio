"""Fleet AI Monetization v7 — track AI platform revenue generation."""
from __future__ import annotations
def fleet_ai_monetization_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    mrr = round(sum(t.get("mrr_usd", 0) for t in trackers), 2)
    arpu = round(sum(t.get("arpu_usd", 0) for t in trackers) / max(len(trackers), 1), 2)
    ltv = round(sum(t.get("ltv_usd", 0) for t in trackers) / max(len(trackers), 1), 2)
    payback_months = round(sum(t.get("payback_m", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "mrr": mrr,
            "arpu": arpu, "ltv": ltv, "payback_m": payback_months, "profitable": payback_months < 12}
