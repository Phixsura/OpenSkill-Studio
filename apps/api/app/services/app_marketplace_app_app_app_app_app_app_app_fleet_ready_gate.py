"""Fleet readiness gate — track deployment readiness gates."""
from __future__ import annotations
def fleet_readiness_gate(deploys: list[dict]) -> dict:
    passed = [d for d in deploys if d.get("gates_passed", False)]
    blocked = [d for d in deploys if d.get("gate_blocked", False)]
    return {"total": len(deploys), "passed": len(passed), "blocked": len(blocked),
            "all_clear": len(blocked) == 0}
