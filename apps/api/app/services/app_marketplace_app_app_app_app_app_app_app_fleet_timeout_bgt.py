"""Fleet timeout budget — track timeout allocation across call chains."""
from __future__ import annotations
def fleet_timeout_budget(chains: list[dict]) -> dict:
    over_budget = [c for c in chains if c.get("actual_ms", 0) > c.get("budget_ms", 5000)]
    avg_util = round(sum(c.get("actual_ms", 0) / max(c.get("budget_ms", 1), 1) for c in chains) / max(len(chains), 1) * 100, 1)
    return {"chains": len(chains), "over_budget": len(over_budget),
            "avg_utilization_pct": avg_util, "healthy": len(over_budget) == 0}
