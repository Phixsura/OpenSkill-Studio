"""Fleet Deploy Gate v9 — track deployment approval gates and checks."""
from __future__ import annotations
def fleet_deploy_gate_v9(gates: list[dict]) -> dict:
    passed = [g for g in gates if g.get("status") == "passed"]
    blocked = [g for g in gates if g.get("status") == "blocked"]
    auto_approved = [g for g in gates if g.get("auto_approved")]
    return {"total": len(gates), "passed": len(passed), "blocked": len(blocked),
            "auto_approved": len(auto_approved), "healthy": len(blocked) == 0}
