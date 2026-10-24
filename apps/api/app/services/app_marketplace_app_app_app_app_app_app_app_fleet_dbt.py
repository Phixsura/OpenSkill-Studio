"""Fleet dbt — track data transformation pipeline health."""
from __future__ import annotations
def fleet_dbt_status(projects: list[dict]) -> dict:
    passing = [p for p in projects if p.get("last_run_status") == "success"]
    failed = [p for p in projects if p.get("last_run_status") == "error"]
    total_models = sum(p.get("models", 0) for p in projects)
    total_tests = sum(p.get("tests", 0) for p in projects)
    return {"projects": len(projects), "passing": len(passing), "failed": len(failed),
            "models": total_models, "tests": total_tests, "healthy": len(failed) == 0}
