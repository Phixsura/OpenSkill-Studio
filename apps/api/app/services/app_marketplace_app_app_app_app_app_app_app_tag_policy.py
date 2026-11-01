"""Resource tagging policy enforcer — ensure all resources are properly tagged."""
from __future__ import annotations

REQUIRED_TAGS = {"environment", "team", "cost_center", "service", "managed_by"}


def enforce_policy(resources: list[dict]) -> dict:
    compliant = 0
    violations = []
    for r in resources:
        tags = set(r.get("tags", {}).keys())
        missing = sorted(REQUIRED_TAGS - tags)
        if not missing:
            compliant += 1
        else:
            violations.append({"resource": r.get("name", ""), "missing_tags": missing})
    total = len(resources)
    return {"total": total, "compliant": compliant, "non_compliant": total - compliant,
            "violations": violations, "compliance_pct": round(compliant / max(total, 1) * 100)}
