"""Fleet Packer — track machine image build status."""
from __future__ import annotations
def fleet_packer_status(builds: list[dict]) -> dict:
    succeeded = [b for b in builds if b.get("status") == "succeeded"]
    failed = [b for b in builds if b.get("status") == "failed"]
    avg_dur = round(sum(b.get("duration_min", 0) for b in succeeded) / max(len(succeeded), 1), 1)
    return {"total": len(builds), "succeeded": len(succeeded), "failed": len(failed),
            "avg_duration_min": avg_dur, "reliable": len(failed) == 0}
