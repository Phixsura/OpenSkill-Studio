"""Fleet AI Summarization — track document and text summarization."""
from __future__ import annotations
def fleet_ai_summarization(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    docs_24h = sum(s.get("docs_24h", 0) for s in services)
    avg_compression = round(sum(s.get("compression_ratio", 0) for s in services) / max(len(services), 1), 1)
    quality = round(sum(s.get("rouge_l", 0) for s in services) / max(len(services), 1), 2)
    return {"services": len(services), "active": len(active), "docs_24h": docs_24h,
            "compression_ratio": avg_compression, "rouge_l": quality, "quality": quality > 0.7}
