"""Fleet Wasp — track full-stack React/Node DSL framework."""
from __future__ import annotations
def fleet_wasp_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("deployed", True)]
    entities = sum(a.get("entities", 0) for a in apps)
    operations = sum(a.get("operations", 0) for a in apps)
    return {"apps": len(apps), "deployed": len(deployed), "entities": entities,
            "operations": operations, "all_deployed": len(deployed) == len(apps)}
