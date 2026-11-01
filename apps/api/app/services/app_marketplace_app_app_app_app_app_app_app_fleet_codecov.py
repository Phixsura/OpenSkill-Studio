"""Fleet Codecov — track test coverage reporting."""
from __future__ import annotations
def fleet_codecov_status(repos: list[dict]) -> dict:
    with_cov = [r for r in repos if r.get("has_codecov", False)]
    avg_cov = round(sum(r.get("coverage_pct", 0) for r in with_cov) / max(len(with_cov), 1), 1)
    declining = [r for r in with_cov if r.get("coverage_trend") == "declining"]
    return {"total": len(repos), "with_codecov": len(with_cov), "avg_coverage": avg_cov,
            "declining": len(declining), "healthy": len(declining) == 0}
