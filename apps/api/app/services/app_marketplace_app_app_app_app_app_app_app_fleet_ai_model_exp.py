"""Fleet AI Model Export — track model format conversion and export."""
from __future__ import annotations
def fleet_ai_model_export(exporters: list[dict]) -> dict:
    active = [e for e in exporters if e.get("active", True)]
    exports_24h = sum(e.get("exports_24h", 0) for e in exporters)
    formats = set()
    for e in exporters:
        formats.update(e.get("formats", []))
    size_gb = round(sum(e.get("size_gb", 0) for e in exporters), 1)
    return {"exporters": len(exporters), "active": len(active), "exports_24h": exports_24h,
            "formats": len(formats), "size_gb": size_gb, "versatile": len(formats) > 3}
