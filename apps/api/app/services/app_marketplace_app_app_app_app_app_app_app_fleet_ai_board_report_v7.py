"""Fleet AI Board Report v7 — track board-level AI platform reporting."""
from __future__ import annotations
def fleet_ai_board_report_v7(reports: list[dict]) -> dict:
    active = [r for r in reports if r.get("active", True)]
    quarterly = sum(r.get("quarterly", 0) for r in reports)
    metrics = sum(r.get("metrics", 0) for r in reports)
    revenue_impact = round(sum(r.get("revenue_impact_usd", 0) for r in reports), 2)
    return {"reports": len(reports), "active": len(active), "quarterly": quarterly,
            "metrics": metrics, "revenue_impact": revenue_impact, "strategic": revenue_impact > 0}
