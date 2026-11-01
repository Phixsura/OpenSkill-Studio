"""Fleet AI Revenue v2 — track AI platform revenue metrics."""
from __future__ import annotations
def fleet_ai_revenue_v2(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    mrr = round(sum(t.get("mrr_usd", 0) for t in trackers), 2)
    arr = round(mrr * 12, 2)
    growth_pct = round(sum(t.get("growth_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    ndrs = round(sum(t.get("ndr_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "mrr": mrr,
            "arr": arr, "growth_pct": growth_pct, "ndr": ndrs, "scaling": growth_pct > 20}
