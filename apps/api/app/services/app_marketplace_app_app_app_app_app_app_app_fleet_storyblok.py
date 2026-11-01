"""Fleet Storyblok — track visual CMS platform."""
from __future__ import annotations
def fleet_storyblok_status(spaces: list[dict]) -> dict:
    active = [s for s in spaces if s.get("active", True)]
    stories = sum(s.get("stories", 0) for s in spaces)
    components = sum(s.get("components", 0) for s in spaces)
    return {"spaces": len(spaces), "active": len(active), "stories": stories,
            "components": components, "all_active": len(active) == len(spaces)}
