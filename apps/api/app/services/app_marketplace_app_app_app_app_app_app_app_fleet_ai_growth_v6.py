"""Fleet AI Growth v6 — track ultimate platform growth trajectory."""
from __future__ import annotations
def fleet_ai_growth_v6(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    mau = sum(t.get("mau", 0) for t in trackers)
    arr = round(sum(t.get("arr_usd", 0) for t in trackers), 2)
    growth = round(sum(t.get("growth_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    ndr = round(sum(t.get("ndr_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "mau": mau,
            "arr": arr, "growth": growth, "ndr": ndr, "scaling": growth > 20}
