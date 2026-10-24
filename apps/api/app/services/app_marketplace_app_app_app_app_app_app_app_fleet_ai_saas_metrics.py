"""Fleet AI SaaS Metrics — track core SaaS business metrics."""
from __future__ import annotations
def fleet_ai_saas_metrics(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    arr = round(sum(t.get("arr_usd", 0) for t in trackers), 2)
    ltv = round(sum(t.get("ltv_usd", 0) for t in trackers) / max(len(trackers), 1), 2)
    cac = round(sum(t.get("cac_usd", 0) for t in trackers) / max(len(trackers), 1), 2)
    ltv_cac = round(ltv / max(cac, 1), 1)
    return {"trackers": len(trackers), "active": len(active), "arr": arr,
            "ltv": ltv, "cac": cac, "ltv_cac": ltv_cac, "efficient": ltv_cac > 3}
