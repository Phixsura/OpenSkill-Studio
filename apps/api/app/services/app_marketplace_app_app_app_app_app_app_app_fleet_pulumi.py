"""Fleet Pulumi — track Pulumi stack health."""
from __future__ import annotations
def fleet_pulumi_status(stacks: list[dict]) -> dict:
    up_to_date = [s for s in stacks if s.get("status") == "up-to-date"]
    pending = [s for s in stacks if s.get("status") == "pending"]
    failed = [s for s in stacks if s.get("status") == "failed"]
    return {"total": len(stacks), "up_to_date": len(up_to_date), "pending": len(pending),
            "failed": len(failed), "healthy": len(failed) == 0}
