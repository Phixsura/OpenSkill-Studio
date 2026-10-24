"""Fleet K8s Upgrade v9 — track Kubernetes version upgrade status."""
from __future__ import annotations
def fleet_k8s_upgrade_v9(clusters: list[dict]) -> dict:
    current = [c for c in clusters if c.get("up_to_date")]
    upgrading = [c for c in clusters if c.get("upgrading")]
    outdated = [c for c in clusters if c.get("outdated")]
    return {"clusters": len(clusters), "current": len(current), "upgrading": len(upgrading),
            "outdated": len(outdated), "healthy": len(outdated) == 0}
