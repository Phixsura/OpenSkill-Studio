"""Fleet AI Output Parser — track structured output extraction from AI."""
from __future__ import annotations
def fleet_ai_output_parser(parsers: list[dict]) -> dict:
    active = [p for p in parsers if p.get("active", True)]
    parsed_24h = sum(p.get("parsed_24h", 0) for p in parsers)
    formats = set()
    for p in parsers:
        formats.update(p.get("formats", []))
    success_pct = round(sum(p.get("success_pct", 0) for p in parsers) / max(len(parsers), 1), 1)
    return {"parsers": len(parsers), "active": len(active), "parsed_24h": parsed_24h,
            "formats": len(formats), "success_pct": success_pct, "reliable": success_pct > 95}
