"""Fleet structured logging — track logging format adoption."""
from __future__ import annotations
def fleet_structured_logging(services: list[dict]) -> dict:
    structured = [s for s in services if s.get("structured", False)]
    json_format = [s for s in services if s.get("format") == "json"]
    pct = round(len(structured) / max(len(services), 1) * 100, 1)
    return {"total": len(services), "structured": len(structured), "json": len(json_format),
            "unstructured": len(services) - len(structured), "mature": pct >= 90}
