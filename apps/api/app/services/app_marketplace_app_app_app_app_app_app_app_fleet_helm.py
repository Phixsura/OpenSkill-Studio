"""Fleet Helm releases — track Helm chart deployment status."""
from __future__ import annotations
def fleet_helm_status(releases: list[dict]) -> dict:
    deployed = [r for r in releases if r.get("status") == "deployed"]
    failed = [r for r in releases if r.get("status") == "failed"]
    pending = [r for r in releases if r.get("status") == "pending-upgrade"]
    return {"total": len(releases), "deployed": len(deployed), "failed": len(failed),
            "pending": len(pending), "healthy": len(failed) == 0}
