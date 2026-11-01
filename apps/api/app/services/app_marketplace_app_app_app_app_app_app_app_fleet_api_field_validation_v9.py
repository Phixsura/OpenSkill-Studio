"""Fleet API Field Validation v9 — track per-field validation rules."""
from __future__ import annotations
def fleet_api_field_validation_v9(rules: list[dict]) -> dict:
    active = [r for r in rules if r.get("active")]
    rejections = sum(r.get("rejections_today", 0) for r in rules)
    fields = sum(r.get("fields_validated", 0) for r in rules)
    return {"rules": len(rules), "active": len(active), "rejections_today": rejections,
            "fields_validated": fields, "healthy": True}
