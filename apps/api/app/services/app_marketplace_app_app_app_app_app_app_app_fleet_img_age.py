"""Fleet container image age — track how old running images are."""
from __future__ import annotations
def fleet_image_age(images: list[dict]) -> dict:
    old = [i for i in images if i.get("age_days", 0) > 30]
    ancient = [i for i in images if i.get("age_days", 0) > 90]
    return {"total": len(images), "old": len(old), "ancient": len(ancient),
            "fresh": len(images) - len(old), "needs_update": len(ancient) > 0}
