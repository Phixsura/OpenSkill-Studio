"""Fleet API Change Log v9 — track API change history and impact."""
from __future__ import annotations
def fleet_api_change_log_v9(changes: list[dict]) -> dict:
    breaking = [c for c in changes if c.get("breaking")]
    non_breaking = [c for c in changes if not c.get("breaking")]
    consumers_notified = sum(c.get("consumers_notified", 0) for c in changes)
    return {"changes": len(changes), "breaking": len(breaking), "non_breaking": len(non_breaking),
            "consumers_notified": consumers_notified, "healthy": len(breaking) == 0}
