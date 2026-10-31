"""Fleet AI Context Compressor — track context window compression techniques."""
from __future__ import annotations
def fleet_ai_context_compressor(compressors: list[dict]) -> dict:
    active = [c for c in compressors if c.get("active", True)]
    compressions_24h = sum(c.get("compressions_24h", 0) for c in compressors)
    ratio = round(sum(c.get("ratio", 0) for c in compressors) / max(len(compressors), 1), 1)
    quality_retained = round(sum(c.get("quality_pct", 0) for c in compressors) / max(len(compressors), 1), 1)
    return {"compressors": len(compressors), "active": len(active), "compressions_24h": compressions_24h,
            "ratio": ratio, "quality_pct": quality_retained, "lossless": quality_retained > 95}
