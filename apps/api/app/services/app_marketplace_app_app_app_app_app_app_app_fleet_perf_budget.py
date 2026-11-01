"""Fleet performance budget — track web vitals budgets."""
from __future__ import annotations
def fleet_perf_budget(pages: list[dict]) -> dict:
    within = [p for p in pages if p.get("lcp_ms", 0) <= 2500 and p.get("cls", 0) <= 0.1]
    over = len(pages) - len(within)
    return {"total": len(pages), "within_budget": len(within), "over_budget": over,
            "compliant": over == 0}
