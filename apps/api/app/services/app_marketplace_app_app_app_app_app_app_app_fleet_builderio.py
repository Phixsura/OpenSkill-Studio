"""Fleet Builder.io — track visual development platform."""
from __future__ import annotations
def fleet_builderio_status(spaces: list[dict]) -> dict:
    active = [s for s in spaces if s.get("active", True)]
    pages = sum(s.get("pages", 0) for s in spaces)
    components = sum(s.get("components", 0) for s in spaces)
    return {"spaces": len(spaces), "active": len(active), "pages": pages,
            "components": components, "all_active": len(active) == len(spaces)}
