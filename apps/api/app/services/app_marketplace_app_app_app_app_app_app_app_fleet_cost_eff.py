"""Fleet cost efficiency — revenue per infrastructure dollar."""
from __future__ import annotations
def fleet_cost_efficiency(revenue: float, infra_cost: float) -> dict:
    ratio = round(revenue / max(infra_cost, 0.01), 2)
    efficient = ratio > 5
    return {"revenue": revenue, "infra_cost": infra_cost, "ratio": ratio,
            "efficient": efficient, "grade": "A" if ratio > 10 else ("B" if ratio > 5 else "C")}
