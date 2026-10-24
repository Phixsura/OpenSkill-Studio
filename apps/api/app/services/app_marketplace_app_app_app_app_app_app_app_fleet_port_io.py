"""Fleet Port.io — track internal developer portal metrics."""
from __future__ import annotations
def fleet_port_io(blueprints: list[dict]) -> dict:
    entities = sum(b.get("entities", 0) for b in blueprints)
    actions = sum(b.get("self_service_actions", 0) for b in blueprints)
    return {"blueprints": len(blueprints), "entities": entities, "actions": actions,
            "mature": len(blueprints) >= 10}
