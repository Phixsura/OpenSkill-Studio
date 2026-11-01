"""Fleet Buildpacks — track Cloud Native Buildpack usage."""
from __future__ import annotations
def fleet_buildpacks_status(apps: list[dict]) -> dict:
    using_bp = [a for a in apps if a.get("uses_buildpacks", False)]
    avg_build = round(sum(a.get("build_sec", 0) for a in using_bp) / max(len(using_bp), 1), 1)
    return {"total": len(apps), "using_buildpacks": len(using_bp),
            "using_dockerfile": len(apps) - len(using_bp),
            "avg_build_sec": avg_build, "modern": len(using_bp) > len(apps) / 2}
