"""Fleet AI Content Generator — track AI-powered content creation."""
from __future__ import annotations
def fleet_ai_content_gen(generators: list[dict]) -> dict:
    active = [g for g in generators if g.get("active", True)]
    content_24h = sum(g.get("content_24h", 0) for g in generators)
    words_generated = sum(g.get("words", 0) for g in generators)
    quality_score = round(sum(g.get("quality", 0) for g in generators) / max(len(generators), 1), 1)
    return {"generators": len(generators), "active": len(active), "content_24h": content_24h,
            "words": words_generated, "quality": quality_score, "creative": quality_score > 80}
