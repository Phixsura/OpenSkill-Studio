"""Fleet platform ROI — calculate return on investment."""
from __future__ import annotations
def fleet_platform_roi(investment: float, savings: float, revenue_uplift: float) -> dict:
    total_return = savings + revenue_uplift
    roi_pct = round((total_return - investment) / max(investment, 0.01) * 100, 1)
    payback_months = round(investment / max(total_return / 12, 0.01), 1) if total_return > 0 else -1
    return {"investment": investment, "total_return": total_return, "roi_pct": roi_pct,
            "payback_months": payback_months, "positive": roi_pct > 0}
