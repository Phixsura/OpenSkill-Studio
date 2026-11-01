"""Fleet API deprecation — track deprecated endpoint usage."""
from __future__ import annotations
def fleet_deprecation_tracker(endpoints: list[dict]) -> dict:
    deprecated = [e for e in endpoints if e.get("deprecated", False)]
    still_used = [e for e in deprecated if e.get("requests_24h", 0) > 0]
    return {"total": len(endpoints), "deprecated": len(deprecated),
            "still_used": len(still_used), "safe_to_remove": len(deprecated) - len(still_used)}
