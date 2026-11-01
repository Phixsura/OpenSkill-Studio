"""Fleet AI Structured Output — track JSON/schema-constrained AI generation."""
from __future__ import annotations
def fleet_ai_structured_output(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    requests_24h = sum(s.get("requests_24h", 0) for s in services)
    valid_pct = round(sum(s.get("valid_pct", 0) for s in services) / max(len(services), 1), 1)
    schemas = sum(s.get("schemas", 0) for s in services)
    return {"services": len(services), "active": len(active), "requests_24h": requests_24h,
            "valid_pct": valid_pct, "schemas": schemas, "reliable": valid_pct > 99}
