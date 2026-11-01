"""Fleet Git Mirror v9 — track repository mirroring across providers."""
from __future__ import annotations
def fleet_git_mirror_v9(mirrors: list[dict]) -> dict:
    synced = [m for m in mirrors if m.get("synced")]
    behind = [m for m in mirrors if m.get("commits_behind", 0) > 0]
    total_repos = len({m.get("repo") for m in mirrors if m.get("repo")})
    return {"mirrors": len(mirrors), "synced": len(synced), "behind": len(behind),
            "unique_repos": total_repos, "healthy": len(behind) == 0}
