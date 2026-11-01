"""Fleet Nx — track Nx workspace build and test metrics."""
from __future__ import annotations
def fleet_nx_status(projects: list[dict]) -> dict:
    affected = [p for p in projects if p.get("affected", False)]
    cached = [p for p in projects if p.get("from_cache", False)]
    avg_build = round(sum(p.get("build_sec", 0) for p in projects) / max(len(projects), 1), 1)
    return {"total_projects": len(projects), "affected": len(affected), "from_cache": len(cached),
            "avg_build_sec": avg_build, "efficient": len(cached) > len(projects) / 2}
