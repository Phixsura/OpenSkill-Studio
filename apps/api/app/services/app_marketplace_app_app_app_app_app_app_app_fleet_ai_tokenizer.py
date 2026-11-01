"""Fleet AI Tokenizer — track text tokenization and vocabulary management."""
from __future__ import annotations
def fleet_ai_tokenizer(tokenizers: list[dict]) -> dict:
    active = [t for t in tokenizers if t.get("active", True)]
    vocab_size = max((t.get("vocab_size", 0) for t in tokenizers), default=0)
    tokens_24h = sum(t.get("tokens_24h", 0) for t in tokenizers)
    compression = round(sum(t.get("compression_ratio", 0) for t in tokenizers) / max(len(tokenizers), 1), 2)
    return {"tokenizers": len(tokenizers), "active": len(active), "vocab_size": vocab_size,
            "tokens_24h": tokens_24h, "compression": compression, "efficient": compression > 3}
