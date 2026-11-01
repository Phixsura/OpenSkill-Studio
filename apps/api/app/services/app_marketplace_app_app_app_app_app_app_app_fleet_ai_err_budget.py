"""Fleet AI Error Budget — track SLO error budget consumption."""
from __future__ import annotations
def fleet_ai_error_budget(budgets: list[dict]) -> dict:
    active = [b for b in budgets if b.get("active", True)]
    remaining_pct = round(sum(b.get("remaining_pct", 0) for b in budgets) / max(len(budgets), 1), 1)
    burn_rate = round(sum(b.get("burn_rate", 0) for b in budgets) / max(len(budgets), 1), 2)
    slos = sum(b.get("slos", 0) for b in budgets)
    return {"budgets": len(budgets), "active": len(active), "remaining_pct": remaining_pct,
            "burn_rate": burn_rate, "slos": slos, "safe": remaining_pct > 50}
