"""Fleet Webhook Transform v9 — track webhook payload transformation."""
from __future__ import annotations
def fleet_webhook_transform_v9(transforms: list[dict]) -> dict:
    active = [t for t in transforms if t.get("active")]
    transformed = sum(t.get("transformed_today", 0) for t in transforms)
    errors = sum(t.get("errors", 0) for t in transforms)
    return {"transforms": len(transforms), "active": len(active), "transformed_today": transformed,
            "errors": errors, "healthy": errors == 0}
