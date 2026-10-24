"""Fleet API Quality Gate v9 — track API quality gates before deployment."""
from __future__ import annotations
def fleet_api_quality_gate_v9(gates: list[dict]) -> dict:
    passed = [g for g in gates if g.get("passed")]
    blocked = [g for g in gates if g.get("blocked")]
    checks = sum(g.get("checks", 0) for g in gates)
    return {"gates": len(gates), "passed": len(passed), "blocked": len(blocked),
            "total_checks": checks, "healthy": len(blocked) == 0}
