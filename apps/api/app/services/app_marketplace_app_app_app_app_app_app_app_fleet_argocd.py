"""Fleet ArgoCD — track GitOps application sync status."""
from __future__ import annotations
def fleet_argocd_sync(apps: list[dict]) -> dict:
    synced = [a for a in apps if a.get("sync_status") == "Synced"]
    healthy = [a for a in apps if a.get("health_status") == "Healthy"]
    degraded = [a for a in apps if a.get("health_status") == "Degraded"]
    return {"total": len(apps), "synced": len(synced), "healthy": len(healthy),
            "degraded": len(degraded), "all_synced": len(synced) == len(apps)}
