"""Fleet Code Coverage v9 — track test coverage across repositories."""
from __future__ import annotations
def fleet_code_coverage_v9(repos: list[dict]) -> dict:
    avg_cov = sum(r.get("coverage_pct", 0) for r in repos) / len(repos) if repos else 0
    above_80 = [r for r in repos if r.get("coverage_pct", 0) >= 80]
    lines_covered = sum(r.get("lines_covered", 0) for r in repos)
    return {"repos": len(repos), "avg_coverage": round(avg_cov, 1), "above_80pct": len(above_80),
            "lines_covered": lines_covered, "healthy": avg_cov >= 80}
