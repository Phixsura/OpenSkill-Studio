"""Fleet AI Document Loader — track multi-format document ingestion."""
from __future__ import annotations
def fleet_ai_document_loader(loaders: list[dict]) -> dict:
    active = [l for l in loaders if l.get("active", True)]
    formats = set()
    for l in loaders:
        formats.update(l.get("formats", []))
    docs_24h = sum(l.get("docs_24h", 0) for l in loaders)
    size_gb = round(sum(l.get("size_gb", 0) for l in loaders), 1)
    return {"loaders": len(loaders), "active": len(active), "formats": len(formats),
            "docs_24h": docs_24h, "size_gb": size_gb, "versatile": len(formats) > 5}
