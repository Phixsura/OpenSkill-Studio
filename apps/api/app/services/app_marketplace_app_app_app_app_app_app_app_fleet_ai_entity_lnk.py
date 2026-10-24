"""Fleet AI Entity Linker — track entity disambiguation and linking."""
from __future__ import annotations
def fleet_ai_entity_linker(linkers: list[dict]) -> dict:
    active = [l for l in linkers if l.get("active", True)]
    entities_24h = sum(l.get("entities_24h", 0) for l in linkers)
    linked = sum(l.get("linked", 0) for l in linkers)
    accuracy = round(sum(l.get("accuracy", 0) for l in linkers) / max(len(linkers), 1), 1)
    return {"linkers": len(linkers), "active": len(active), "entities_24h": entities_24h,
            "linked": linked, "accuracy": accuracy, "accurate": accuracy > 85}
