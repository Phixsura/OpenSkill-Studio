"""Fleet Helm Release v9 — track Helm chart releases and revisions."""
from __future__ import annotations
def fleet_helm_release_v9(releases: list[dict]) -> dict:
    deployed = [r for r in releases if r.get("status") == "deployed"]
    failed = [r for r in releases if r.get("status") == "failed"]
    revisions = sum(r.get("revision", 1) for r in releases)
    return {"releases": len(releases), "deployed": len(deployed), "failed": len(failed),
            "total_revisions": revisions, "healthy": len(failed) == 0}
