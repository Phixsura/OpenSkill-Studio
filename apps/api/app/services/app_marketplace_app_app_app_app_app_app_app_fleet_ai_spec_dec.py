"""Fleet AI Speculative Decoding — track draft-verify decoding acceleration."""
from __future__ import annotations
def fleet_ai_spec_decoding(decoders: list[dict]) -> dict:
    active = [d for d in decoders if d.get("active", True)]
    tokens_24h = sum(d.get("tokens_24h", 0) for d in decoders)
    acceptance_rate = round(sum(d.get("acceptance_pct", 0) for d in decoders) / max(len(decoders), 1), 1)
    speedup = round(sum(d.get("speedup_x", 0) for d in decoders) / max(len(decoders), 1), 1)
    return {"decoders": len(decoders), "active": len(active), "tokens_24h": tokens_24h,
            "acceptance_rate": acceptance_rate, "speedup_x": speedup, "fast": speedup > 2}
