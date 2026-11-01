"""Fleet lint score — aggregate linting compliance."""
from __future__ import annotations
def fleet_lint_score(repos: list[dict]) -> dict:
    clean = [r for r in repos if r.get("lint_errors", 0) == 0]
    total_errors = sum(r.get("lint_errors", 0) for r in repos)
    pct = round(len(clean) / max(len(repos), 1) * 100, 1)
    return {"total_repos": len(repos), "clean": len(clean), "total_errors": total_errors,
            "clean_pct": pct, "excellent": pct >= 95}
