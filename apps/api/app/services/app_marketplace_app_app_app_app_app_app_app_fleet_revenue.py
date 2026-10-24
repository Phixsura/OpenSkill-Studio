"""Fleet revenue metrics — track platform revenue KPIs."""
from __future__ import annotations
def fleet_revenue_metrics(metrics: dict) -> dict:
    mrr = metrics.get("mrr", 0)
    arr = round(mrr * 12, 2)
    growth = metrics.get("mrr_growth_pct", 0)
    ltv = metrics.get("avg_ltv", 0)
    cac = metrics.get("avg_cac", 0)
    ltv_cac = round(ltv / max(cac, 0.01), 2)
    return {"mrr": mrr, "arr": arr, "mrr_growth_pct": growth,
            "ltv_cac_ratio": ltv_cac, "unit_economics_healthy": ltv_cac >= 3}
