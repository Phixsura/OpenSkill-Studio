"""Fleet Infra Drift v9 — track IaC drift detection and remediation."""
from __future__ import annotations
def fleet_infra_drift_v9(stacks: list[dict]) -> dict:
    drifted = [s for s in stacks if s.get("drifted")]
    auto_fixed = [s for s in stacks if s.get("auto_remediated")]
    resources_total = sum(s.get("resources", 0) for s in stacks)
    return {"stacks": len(stacks), "drifted": len(drifted), "auto_fixed": len(auto_fixed),
            "total_resources": resources_total, "healthy": len(drifted) == 0}
