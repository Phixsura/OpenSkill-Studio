"""Mesh error budget — track error budgets across mesh services."""
from __future__ import annotations
def check_mesh_err_budget(services: list[dict]) -> dict:
    exhausted = [s for s in services if s.get("budget_consumed_pct", 0) >= 100]
    return {"total": len(services), "exhausted": len(exhausted),
            "healthy": len(services) - len(exhausted), "all_within": len(exhausted) == 0}
