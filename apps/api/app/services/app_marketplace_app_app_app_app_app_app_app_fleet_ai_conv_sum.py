"""Fleet AI Conversation Summarizer — track AI conversation summarization."""
from __future__ import annotations
def fleet_ai_conversation_summarizer(summarizers: list[dict]) -> dict:
    active = [s for s in summarizers if s.get("active", True)]
    summarized_24h = sum(s.get("summarized_24h", 0) for s in summarizers)
    compression = round(sum(s.get("compression", 0) for s in summarizers) / max(len(summarizers), 1), 1)
    retention = round(sum(s.get("retention_pct", 0) for s in summarizers) / max(len(summarizers), 1), 1)
    return {"summarizers": len(summarizers), "active": len(active), "summarized_24h": summarized_24h,
            "compression": compression, "retention": retention, "accurate": retention > 90}
