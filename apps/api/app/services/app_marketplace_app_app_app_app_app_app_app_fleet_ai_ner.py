"""Fleet AI NER — track named entity recognition."""
from __future__ import annotations
def fleet_ai_ner(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    docs_24h = sum(s.get("docs_24h", 0) for s in services)
    entities_found = sum(s.get("entities_24h", 0) for s in services)
    return {"services": len(services), "active": len(active), "docs_24h": docs_24h,
            "entities_24h": entities_found, "productive": entities_found > 0}
