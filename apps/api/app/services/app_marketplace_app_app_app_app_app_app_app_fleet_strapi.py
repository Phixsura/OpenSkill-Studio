"""Fleet Strapi — track headless CMS platform."""
from __future__ import annotations
def fleet_strapi_status(instances: list[dict]) -> dict:
    running = [i for i in instances if i.get("running", True)]
    content_types = sum(i.get("content_types", 0) for i in instances)
    entries = sum(i.get("entries", 0) for i in instances)
    return {"instances": len(instances), "running": len(running), "content_types": content_types,
            "entries": entries, "all_running": len(running) == len(instances)}
