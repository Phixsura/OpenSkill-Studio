"""Fleet AI Unit Economics v8 — track per-customer unit economics."""
from __future__ import annotations
def fleet_ai_unit_economics_v8(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    ltv = round(sum(t.get("ltv_usd", 0) for t in trackers) / max(len(trackers), 1), 2)
    cac = round(sum(t.get("cac_usd", 0) for t in trackers) / max(len(trackers), 1), 2)
    ltv_cac = round(ltv / max(cac, 1), 1)
    payback = round(sum(t.get("payback_m", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "ltv": ltv,
            "cac": cac, "ltv_cac": ltv_cac, "payback_m": payback, "efficient": ltv_cac > 3}
