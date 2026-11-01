"""Fleet AI Text Extractor — track AI-powered text extraction from media."""
from __future__ import annotations
def fleet_ai_text_extractor(extractors: list[dict]) -> dict:
    active = [e for e in extractors if e.get("active", True)]
    extracted_24h = sum(e.get("extracted_24h", 0) for e in extractors)
    media_types = set()
    for e in extractors:
        media_types.update(e.get("types", []))
    accuracy = round(sum(e.get("accuracy", 0) for e in extractors) / max(len(extractors), 1), 1)
    return {"extractors": len(extractors), "active": len(active), "extracted_24h": extracted_24h,
            "types": len(media_types), "accuracy": accuracy, "versatile": len(media_types) > 3}
