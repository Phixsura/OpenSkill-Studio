"""Fleet service level budget — remaining budget per SLO."""
from __future__ import annotations
def fleet_sl_budget(slos: list[dict]) -> dict:
    exhausted = [s for s in slos if s.get("remaining_pct", 100) <= 0]
    low = [s for s in slos if 0 < s.get("remaining_pct", 100) <= 20]
    return {"total": len(slos), "exhausted": len(exhausted), "low": len(low),
            "healthy": len(slos) - len(exhausted) - len(low), "alert": len(exhausted) > 0}
