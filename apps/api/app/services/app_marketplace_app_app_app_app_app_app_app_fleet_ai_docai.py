"""Fleet AI Document Understanding — track intelligent document processing."""
from __future__ import annotations
def fleet_ai_docai(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    pages_24h = sum(s.get("pages_24h", 0) for s in services)
    fields_extracted = sum(s.get("fields_24h", 0) for s in services)
    return {"services": len(services), "active": len(active), "pages_24h": pages_24h,
            "fields_24h": fields_extracted, "all_active": len(active) == len(services)}
