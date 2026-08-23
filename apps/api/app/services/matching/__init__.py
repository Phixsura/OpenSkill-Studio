"""Shared matching pipeline (ADR-012) — built once, consumed by pack/creator/
template matching and both composers.

Pipeline: S1 eligibility → S2 hard constraints → S3 linear scoring.
S4 (semantic) and S5 (LLM rerank) are Phase-2 sockets; config carries
`semantic_enabled: false` reserved keys.
"""

from app.services.matching.engine import ENGINE_VERSION, MatchingEngine, MatchSpec

__all__ = ["ENGINE_VERSION", "MatchingEngine", "MatchSpec"]
