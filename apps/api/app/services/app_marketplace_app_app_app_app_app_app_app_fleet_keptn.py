"""Fleet Keptn — track application lifecycle orchestration."""
from __future__ import annotations
def fleet_keptn_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("phase") == "deployed"]
    evaluating = [a for a in apps if a.get("phase") == "evaluating"]
    failed = [a for a in apps if a.get("phase") == "failed"]
    return {"total": len(apps), "deployed": len(deployed), "evaluating": len(evaluating),
            "failed": len(failed), "healthy": len(failed) == 0}
