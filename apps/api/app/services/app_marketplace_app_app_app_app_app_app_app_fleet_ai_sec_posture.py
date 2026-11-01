"""Fleet AI Security Posture — track overall AI security stance."""
from __future__ import annotations
def fleet_ai_security_posture(assessors: list[dict]) -> dict:
    active = [a for a in assessors if a.get("active", True)]
    score = round(sum(a.get("score", 0) for a in assessors) / max(len(assessors), 1), 1)
    vulnerabilities = sum(a.get("vulns", 0) for a in assessors)
    controls = sum(a.get("controls", 0) for a in assessors)
    compliance = round(sum(a.get("compliance_pct", 0) for a in assessors) / max(len(assessors), 1), 1)
    return {"assessors": len(assessors), "active": len(active), "score": score,
            "vulns": vulnerabilities, "controls": controls, "compliance": compliance, "strong": score > 90}
