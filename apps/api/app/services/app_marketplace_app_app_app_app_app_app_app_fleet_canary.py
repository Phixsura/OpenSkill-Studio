"""Fleet canary deploy — track canary deployment status."""
from __future__ import annotations
def fleet_canary_status(deploys: list[dict]) -> dict:
    active = [d for d in deploys if d.get("phase") == "canary"]
    failed = [d for d in deploys if d.get("phase") == "failed"]
    promoted = [d for d in deploys if d.get("phase") == "promoted"]
    return {"total": len(deploys), "active_canaries": len(active),
            "failed": len(failed), "promoted": len(promoted)}
