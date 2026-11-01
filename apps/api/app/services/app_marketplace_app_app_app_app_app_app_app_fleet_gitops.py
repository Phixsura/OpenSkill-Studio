"""Fleet GitOps sync — track GitOps reconciliation status."""
from __future__ import annotations
def fleet_gitops_sync(apps: list[dict]) -> dict:
    synced = [a for a in apps if a.get("sync_status") == "synced"]
    out_of_sync = [a for a in apps if a.get("sync_status") == "out-of-sync"]
    return {"total": len(apps), "synced": len(synced), "out_of_sync": len(out_of_sync),
            "all_synced": len(synced) == len(apps)}
