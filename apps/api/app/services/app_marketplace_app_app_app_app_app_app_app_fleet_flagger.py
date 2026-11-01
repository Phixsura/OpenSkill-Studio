"""Fleet Flagger — track progressive delivery automation."""
from __future__ import annotations
def fleet_flagger_status(canaries: list[dict]) -> dict:
    progressing = [c for c in canaries if c.get("phase") == "Progressing"]
    succeeded = [c for c in canaries if c.get("phase") == "Succeeded"]
    failed = [c for c in canaries if c.get("phase") == "Failed"]
    return {"total": len(canaries), "progressing": len(progressing), "succeeded": len(succeeded),
            "failed": len(failed), "healthy": len(failed) == 0}
