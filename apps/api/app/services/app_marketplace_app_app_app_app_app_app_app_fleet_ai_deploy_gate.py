"""Fleet AI Deployment Gate — track pre-deployment quality gates."""
from __future__ import annotations
def fleet_ai_deployment_gate(gates: list[dict]) -> dict:
    active = [g for g in gates if g.get("active", True)]
    evaluations_24h = sum(g.get("evals_24h", 0) for g in gates)
    passed = sum(g.get("passed", 0) for g in gates)
    blocked = sum(g.get("blocked", 0) for g in gates)
    checks = sum(g.get("checks", 0) for g in gates)
    return {"gates": len(gates), "active": len(active), "evals_24h": evaluations_24h,
            "passed": passed, "blocked": blocked, "checks": checks, "guarding": checks > 0}
