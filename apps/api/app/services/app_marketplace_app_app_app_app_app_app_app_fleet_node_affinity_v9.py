"""Fleet Node Affinity v9 — track K8s node affinity and anti-affinity rules."""
from __future__ import annotations
def fleet_node_affinity_v9(rules: list[dict]) -> dict:
    required = [r for r in rules if r.get("type") == "required"]
    preferred = [r for r in rules if r.get("type") == "preferred"]
    violations = [r for r in rules if r.get("violated")]
    return {"rules": len(rules), "required": len(required), "preferred": len(preferred),
            "violations": len(violations), "healthy": len(violations) == 0}
