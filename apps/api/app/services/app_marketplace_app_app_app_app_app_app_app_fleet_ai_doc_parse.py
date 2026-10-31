"""Fleet AI Document Parsing — track intelligent document extraction."""
from __future__ import annotations
def fleet_ai_doc_parsing(parsers: list[dict]) -> dict:
    active = [p for p in parsers if p.get("active", True)]
    docs_24h = sum(p.get("docs_24h", 0) for p in parsers)
    fields_extracted = sum(p.get("fields", 0) for p in parsers)
    accuracy = round(sum(p.get("accuracy", 0) for p in parsers) / max(len(parsers), 1), 1)
    return {"parsers": len(parsers), "active": len(active), "docs_24h": docs_24h,
            "fields": fields_extracted, "accuracy": accuracy, "reliable": accuracy > 95}
