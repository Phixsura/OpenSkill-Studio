"""Fleet SLO burn window — multi-window SLO burn rate alerting."""
from __future__ import annotations
def fleet_slo_burn_window(slo: dict) -> dict:
    budget = 1 - slo.get("target", 0.999)
    consumed = slo.get("errors", 0) / max(slo.get("total", 1), 1)
    burn = round(consumed / max(budget, 0.0001), 2)
    return {"target": slo.get("target", 0.999), "burn_rate": burn,
            "budget_remaining_pct": round(max(0, (1 - consumed / max(budget, 0.0001)) * 100), 1),
            "alert": burn > 1}
