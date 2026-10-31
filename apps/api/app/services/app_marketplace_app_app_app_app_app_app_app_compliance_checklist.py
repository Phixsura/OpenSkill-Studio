"""Compliance checklist engine — SOC2, GDPR, HIPAA readiness tracking."""
from __future__ import annotations

FRAMEWORKS = {
    "soc2": [
        {"id": "s1", "control": "Access Control", "description": "Enforce RBAC"},
        {"id": "s2", "control": "Encryption", "description": "Encrypt data at rest and in transit"},
        {"id": "s3", "control": "Audit Logging", "description": "Log all access events"},
        {"id": "s4", "control": "Incident Response", "description": "Document IR procedures"},
        {"id": "s5", "control": "Change Management", "description": "Track all system changes"},
    ],
    "gdpr": [
        {"id": "g1", "control": "Data Mapping", "description": "Map all PII data flows"},
        {"id": "g2", "control": "Consent Management", "description": "Record user consent"},
        {"id": "g3", "control": "Right to Erasure", "description": "Enable data deletion"},
        {"id": "g4", "control": "DPO Appointment", "description": "Designate data protection officer"},
    ],
}


def get_checklist(framework: str) -> dict:
    controls = FRAMEWORKS.get(framework, [])
    return {"framework": framework, "controls": controls, "total": len(controls)}


def evaluate_compliance(framework: str, completed: list[str]) -> dict:
    controls = FRAMEWORKS.get(framework, [])
    results = []
    for c in controls:
        done = c["id"] in completed
        results.append({**c, "completed": done})
    done_count = sum(1 for r in results if r["completed"])
    total = len(results)
    pct = round(done_count / max(total, 1) * 100)
    return {
        "framework": framework, "results": results,
        "completed": done_count, "total": total,
        "compliance_pct": pct, "compliance_display": f"{pct}%",
        "ready": pct == 100,
        "status": "compliant" if pct == 100 else "in_progress" if pct > 0 else "not_started",
    }
