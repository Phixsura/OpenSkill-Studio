"""Fleet Tokenizer — track tokenization service health."""
from __future__ import annotations
def fleet_tokenizer_status(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    tokens_24h = sum(s.get("tokens_24h", 0) for s in services)
    vocabularies = sum(s.get("vocabularies", 0) for s in services)
    return {"services": len(services), "active": len(active), "tokens_24h": tokens_24h,
            "vocabularies": vocabularies, "all_active": len(active) == len(services)}
