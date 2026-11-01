"""Fleet AI Readiness Gate — track AI service readiness verification."""
from __future__ import annotations
def fleet_ai_readiness_gate(gates: list[dict]) -> dict:
    active = [g for g in gates if g.get("active", True)]
    services = sum(g.get("services", 0) for g in gates)
    ready = sum(g.get("ready", 0) for g in gates)
    checks = sum(g.get("checks", 0) for g in gates)
    return {"gates": len(gates), "active": len(active), "services": services,
            "ready": ready, "checks": checks, "all_ready": ready == services}
