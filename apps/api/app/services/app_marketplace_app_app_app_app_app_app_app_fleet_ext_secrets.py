"""Fleet External Secrets — track ESO sync status."""
from __future__ import annotations
def fleet_external_secrets(stores: list[dict]) -> dict:
    synced = [s for s in stores if s.get("synced", True)]
    failed = [s for s in stores if s.get("status") == "SecretSyncedError"]
    return {"total": len(stores), "synced": len(synced), "failed": len(failed),
            "healthy": len(failed) == 0}
