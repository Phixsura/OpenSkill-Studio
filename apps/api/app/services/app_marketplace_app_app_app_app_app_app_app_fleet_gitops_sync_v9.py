"""Fleet GitOps Sync v9 — track Git-based deployment reconciliation."""
from __future__ import annotations
def fleet_gitops_sync_v9(repos: list[dict]) -> dict:
    synced = [r for r in repos if r.get("synced", True)]
    out_of_sync = [r for r in repos if not r.get("synced", True)]
    commits_behind = sum(r.get("commits_behind", 0) for r in repos)
    return {"repos": len(repos), "synced": len(synced), "out_of_sync": len(out_of_sync),
            "commits_behind": commits_behind, "healthy": len(out_of_sync) == 0}
