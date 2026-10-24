"""Fleet error budget burn — track burn rate against budget."""
from __future__ import annotations
def fleet_err_budget_burn(services: list[dict]) -> dict:
    fast_burn = [s for s in services if s.get("burn_rate", 0) > 10]
    slow_burn = [s for s in services if 1 < s.get("burn_rate", 0) <= 10]
    return {"total": len(services), "fast_burn": len(fast_burn),
            "slow_burn": len(slow_burn), "alert": len(fast_burn) > 0}
