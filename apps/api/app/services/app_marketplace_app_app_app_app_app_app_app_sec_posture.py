"""Security posture assessment — evaluate overall security health."""
from __future__ import annotations

CONTROLS = {
    "mfa_enabled": {"weight": 15, "category": "identity"},
    "encryption_at_rest": {"weight": 15, "category": "data"},
    "encryption_in_transit": {"weight": 15, "category": "data"},
    "vulnerability_scanning": {"weight": 10, "category": "testing"},
    "dependency_auditing": {"weight": 10, "category": "supply_chain"},
    "audit_logging": {"weight": 10, "category": "monitoring"},
    "incident_response_plan": {"weight": 10, "category": "operations"},
    "secrets_rotation": {"weight": 10, "category": "secrets"},
    "network_segmentation": {"weight": 5, "category": "network"},
}


def assess_posture(implemented: list[str]) -> dict:
    score = 0
    results = []
    for control, info in CONTROLS.items():
        passed = control in implemented
        if passed:
            score += info["weight"]
        results.append({"control": control, "passed": passed, **info})
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D"
    return {"score": score, "grade": grade, "controls": results,
            "implemented": len(implemented), "total": len(CONTROLS),
            "max_score": 100}
