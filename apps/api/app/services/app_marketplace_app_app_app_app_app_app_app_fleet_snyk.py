"""Fleet Snyk — track application security testing."""
from __future__ import annotations
def fleet_snyk_status(projects: list[dict]) -> dict:
    clean = [p for p in projects if p.get("critical", 0) == 0 and p.get("high", 0) == 0]
    total_issues = sum(p.get("critical", 0) + p.get("high", 0) + p.get("medium", 0) for p in projects)
    critical = sum(p.get("critical", 0) for p in projects)
    return {"total": len(projects), "clean": len(clean), "total_issues": total_issues,
            "critical": critical, "secure": critical == 0}
