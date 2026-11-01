"""Fleet AI Investor v7 — track AI platform investor metrics."""
from __future__ import annotations
def fleet_ai_investor_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    arr = round(sum(t.get("arr_usd", 0) for t in trackers), 2)
    growth = round(sum(t.get("growth_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    ndr = round(sum(t.get("ndr_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    rule_of_40 = round(growth + sum(t.get("margin_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "arr": arr,
            "growth": growth, "ndr": ndr, "rule_of_40": rule_of_40, "elite": rule_of_40 > 60}
