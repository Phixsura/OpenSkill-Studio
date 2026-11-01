"""Fleet AI Platform Growth — track platform adoption and growth metrics."""
from __future__ import annotations
def fleet_ai_platform_growth(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    mau = sum(t.get("mau", 0) for t in trackers)
    mrr_usd = round(sum(t.get("mrr_usd", 0) for t in trackers), 2)
    growth_pct = round(sum(t.get("growth_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    churn_pct = round(sum(t.get("churn_pct", 0) for t in trackers) / max(len(trackers), 1), 2)
    return {"trackers": len(trackers), "active": len(active), "mau": mau,
            "mrr_usd": mrr_usd, "growth_pct": growth_pct, "churn_pct": churn_pct, "scaling": growth_pct > 10}
