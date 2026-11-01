"""Fleet Error Budget v9 — track SLO error budget burn rate."""
from __future__ import annotations
def fleet_error_budget_v9(slos: list[dict]) -> dict:
    burning_fast = [s for s in slos if s.get("burn_rate", 0) > 1.0]
    remaining = sum(s.get("budget_pct", 100) for s in slos) / len(slos) if slos else 0
    alerts_fired = sum(s.get("alerts", 0) for s in slos)
    return {"slos": len(slos), "burning_fast": len(burning_fast), "avg_remaining_pct": round(remaining, 1),
            "alerts_fired": alerts_fired, "healthy": len(burning_fast) == 0}
