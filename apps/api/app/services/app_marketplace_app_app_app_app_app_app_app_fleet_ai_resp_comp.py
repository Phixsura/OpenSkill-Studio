"""Fleet AI Response Compressor — track AI response payload compression."""
from __future__ import annotations
def fleet_ai_response_compressor(compressors: list[dict]) -> dict:
    active = [c for c in compressors if c.get("active", True)]
    responses_24h = sum(c.get("responses_24h", 0) for c in compressors)
    compression_ratio = round(sum(c.get("ratio", 0) for c in compressors) / max(len(compressors), 1), 1)
    bandwidth_saved_gb = round(sum(c.get("saved_gb", 0) for c in compressors), 1)
    return {"compressors": len(compressors), "active": len(active), "responses_24h": responses_24h,
            "ratio": compression_ratio, "saved_gb": bandwidth_saved_gb, "compressing": compression_ratio > 1}
