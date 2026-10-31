"""Fleet AI Model Import — track model ingestion and validation."""
from __future__ import annotations
def fleet_ai_model_import(importers: list[dict]) -> dict:
    active = [i for i in importers if i.get("active", True)]
    imports_24h = sum(i.get("imports_24h", 0) for i in importers)
    validated = sum(i.get("validated", 0) for i in importers)
    rejected = sum(i.get("rejected", 0) for i in importers)
    return {"importers": len(importers), "active": len(active), "imports_24h": imports_24h,
            "validated": validated, "rejected": rejected, "strict": rejected >= 0}
