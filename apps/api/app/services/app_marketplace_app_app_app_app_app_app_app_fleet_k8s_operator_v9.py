"""Fleet K8s Operator v9 — track custom Kubernetes operator health."""
from __future__ import annotations
def fleet_k8s_operator_v9(operators: list[dict]) -> dict:
    running = [o for o in operators if o.get("status") == "running"]
    reconciles = sum(o.get("reconciles_per_min", 0) for o in operators)
    errors = sum(o.get("errors", 0) for o in operators)
    return {"operators": len(operators), "running": len(running), "reconciles_per_min": reconciles,
            "errors": errors, "healthy": errors == 0}
