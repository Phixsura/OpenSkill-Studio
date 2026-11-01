"""Fleet Harbor — track Harbor registry projects and quotas."""
from __future__ import annotations
def fleet_harbor_status(projects: list[dict]) -> dict:
    total_repos = sum(p.get("repos", 0) for p in projects)
    total_artifacts = sum(p.get("artifacts", 0) for p in projects)
    over_quota = [p for p in projects if p.get("over_quota", False)]
    return {"projects": len(projects), "repos": total_repos, "artifacts": total_artifacts,
            "over_quota": len(over_quota), "healthy": len(over_quota) == 0}
