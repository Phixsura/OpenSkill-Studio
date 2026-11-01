"""Fleet Compliance Report v9 — track regulatory compliance report generation."""
from __future__ import annotations
def fleet_compliance_report_v9(reports: list[dict]) -> dict:
    generated = [r for r in reports if r.get("generated")]
    frameworks = len({r.get("framework") for r in reports if r.get("framework")})
    findings = sum(r.get("findings", 0) for r in reports)
    return {"reports": len(reports), "generated": len(generated), "frameworks": frameworks,
            "total_findings": findings, "healthy": findings == 0}
