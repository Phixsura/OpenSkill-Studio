"""Fleet AI Named Entity Recognition — track entity extraction pipelines."""
from __future__ import annotations
def fleet_ai_ner(extractors: list[dict]) -> dict:
    active = [e for e in extractors if e.get("active", True)]
    docs_24h = sum(e.get("docs_24h", 0) for e in extractors)
    entities_found = sum(e.get("entities_found", 0) for e in extractors)
    entity_types = sum(e.get("entity_types", 0) for e in extractors)
    f1 = round(sum(e.get("f1", 0) for e in extractors) / max(len(extractors), 1), 2)
    return {"extractors": len(extractors), "active": len(active), "docs_24h": docs_24h,
            "entities_found": entities_found, "entity_types": entity_types, "f1": f1, "accurate": f1 > 0.9}
