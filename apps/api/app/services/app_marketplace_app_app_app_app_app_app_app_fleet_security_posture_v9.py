"""Fleet Security Posture v9 — track overall security posture score."""
from __future__ import annotations
def fleet_security_posture_v9(domains: list[dict]) -> dict:
    scores = [d.get("score", 0) for d in domains]
    avg = sum(scores) / len(scores) if scores else 0
    critical_findings = sum(d.get("critical", 0) for d in domains)
    high_findings = sum(d.get("high", 0) for d in domains)
    return {"domains": len(domains), "avg_score": round(avg, 1), "critical": critical_findings,
            "high": high_findings, "healthy": critical_findings == 0}
