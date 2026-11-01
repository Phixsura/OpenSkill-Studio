"""Fleet API Content Negotiation v9 — track content type negotiation."""
from __future__ import annotations
def fleet_api_content_negotiation_v9(endpoints: list[dict]) -> dict:
    json_only = [e for e in endpoints if e.get("content_type") == "json"]
    multi_format = [e for e in endpoints if e.get("multi_format")]
    xml_support = [e for e in endpoints if e.get("xml_support")]
    return {"endpoints": len(endpoints), "json_only": len(json_only), "multi_format": len(multi_format),
            "xml_support": len(xml_support), "healthy": True}
