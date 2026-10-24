"""Fleet API Deprecation v9 — track deprecated API endpoint migration."""
from __future__ import annotations
def fleet_api_deprecation_v9(endpoints: list[dict]) -> dict:
    deprecated = [e for e in endpoints if e.get("deprecated")]
    migrated = [e for e in endpoints if e.get("migrated")]
    consumers_left = sum(e.get("remaining_consumers", 0) for e in deprecated)
    return {"total": len(endpoints), "deprecated": len(deprecated), "migrated": len(migrated),
            "remaining_consumers": consumers_left, "healthy": consumers_left == 0}
