"""Security policy enforcer — enforce security policies on resources."""
from __future__ import annotations

POLICIES = {
    "require_mfa": {"description": "Require multi-factor authentication", "severity": "high"},
    "no_public_access": {"description": "No public access to resources", "severity": "critical"},
    "encrypt_at_rest": {"description": "Encrypt all data at rest", "severity": "high"},
    "rotate_secrets": {"description": "Rotate secrets every 90 days", "severity": "medium"},
    "audit_logging": {"description": "Enable audit logging", "severity": "high"},
    "min_password_length": {"description": "Minimum 12 character passwords", "severity": "medium"},
}


def check_compliance(resource: dict, enabled_policies: list[str]) -> dict:
    violations = []
    for policy_id in enabled_policies:
        policy = POLICIES.get(policy_id)
        if not policy:
            continue
        compliant = resource.get(f"policy_{policy_id}", False)
        if not compliant:
            violations.append({"policy": policy_id, **policy})
    return {"resource": resource.get("name", ""), "violations": violations,
            "violation_count": len(violations), "compliant": len(violations) == 0,
            "checked": len(enabled_policies)}


def risk_score(violations: list[dict]) -> dict:
    severity_scores = {"critical": 10, "high": 5, "medium": 2, "low": 1}
    score = sum(severity_scores.get(v.get("severity", "low"), 1) for v in violations)
    level = "critical" if score >= 15 else "high" if score >= 10 else "medium" if score >= 5 else "low"
    return {"score": score, "level": level, "max_possible": sum(severity_scores.values()) * len(violations) if violations else 0}
