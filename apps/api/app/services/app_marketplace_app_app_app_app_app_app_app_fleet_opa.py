"""Fleet OPA policy — track Open Policy Agent decisions."""
from __future__ import annotations
def fleet_opa_decisions(policies: list[dict]) -> dict:
    total_eval = sum(p.get("evaluations", 0) for p in policies)
    denied = sum(p.get("denied", 0) for p in policies)
    avg_latency = round(sum(p.get("latency_ms", 0) for p in policies) / max(len(policies), 1), 1)
    return {"policies": len(policies), "total_evaluations": total_eval,
            "denied": denied, "avg_latency_ms": avg_latency}
