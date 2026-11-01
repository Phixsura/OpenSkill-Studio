"""Fleet AI Watermark — track AI-generated content watermarking."""
from __future__ import annotations
def fleet_ai_watermark(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    watermarked_24h = sum(s.get("watermarked_24h", 0) for s in systems)
    detected_24h = sum(s.get("detected_24h", 0) for s in systems)
    detection_rate = round(detected_24h / max(watermarked_24h, 1) * 100, 1)
    return {"systems": len(systems), "active": len(active), "watermarked_24h": watermarked_24h,
            "detected_24h": detected_24h, "detection_rate": detection_rate}
