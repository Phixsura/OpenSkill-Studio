"""Fleet Compliance Posture v9 — track overall compliance posture score."""
from __future__ import annotations
def fleet_compliance_posture_v9(domains: list[dict]) -> dict:
    scores = [d.get("score", 0) for d in domains]
    avg = sum(scores) / len(scores) if scores else 0
    frameworks = len({d.get("framework") for d in domains if d.get("framework")})
    findings = sum(d.get("open_findings", 0) for d in domains)
    return {"domains": len(domains), "avg_score": round(avg, 1), "frameworks": frameworks,
            "open_findings": findings, "healthy": findings == 0}
