"""Fleet AI Summarizer — track document summarization."""
from __future__ import annotations
def fleet_ai_summarizer(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    docs_summarized = sum(s.get("docs_24h", 0) for s in services)
    avg_compression = round(sum(s.get("compression_ratio", 0) for s in services) / max(len(services), 1), 1)
    return {"services": len(services), "active": len(active), "docs_24h": docs_summarized,
            "avg_compression": avg_compression, "all_active": len(active) == len(services)}
