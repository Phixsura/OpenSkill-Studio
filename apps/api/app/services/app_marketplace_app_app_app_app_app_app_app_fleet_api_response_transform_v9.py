"""Fleet API Response Transform v9 — track response transformation rules."""
from __future__ import annotations
def fleet_api_response_transform_v9(transforms: list[dict]) -> dict:
    active = [t for t in transforms if t.get("active")]
    applied = sum(t.get("applied_today", 0) for t in transforms)
    errors = sum(t.get("errors", 0) for t in transforms)
    return {"transforms": len(transforms), "active": len(active), "applied_today": applied,
            "errors": errors, "healthy": errors == 0}
