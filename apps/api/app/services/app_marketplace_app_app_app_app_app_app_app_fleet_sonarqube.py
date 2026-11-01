"""Fleet SonarQube — track code quality gates."""
from __future__ import annotations
def fleet_sonarqube_status(projects: list[dict]) -> dict:
    passing = [p for p in projects if p.get("quality_gate") == "OK"]
    failing = [p for p in projects if p.get("quality_gate") == "ERROR"]
    avg_coverage = round(sum(p.get("coverage_pct", 0) for p in projects) / max(len(projects), 1), 1)
    return {"total": len(projects), "passing": len(passing), "failing": len(failing),
            "avg_coverage": avg_coverage, "all_passing": len(passing) == len(projects)}
