"""Fleet AI Extraction — track entity/data extraction."""
from __future__ import annotations
def fleet_ai_extraction(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    docs_processed = sum(s.get("docs_24h", 0) for s in services)
    entities_extracted = sum(s.get("entities_24h", 0) for s in services)
    return {"services": len(services), "active": len(active), "docs_24h": docs_processed,
            "entities_24h": entities_extracted, "all_active": len(active) == len(services)}
