"""Fleet AI Revenue v8 — track ultimate platform revenue metrics."""
from __future__ import annotations
def fleet_ai_revenue_v8(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    mrr = round(sum(t.get("mrr_usd", 0) for t in trackers), 2)
    ndr = round(sum(t.get("ndr_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    gross_margin = round(sum(t.get("margin_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "mrr": mrr,
            "ndr": ndr, "margin": gross_margin, "efficient": gross_margin > 70}
