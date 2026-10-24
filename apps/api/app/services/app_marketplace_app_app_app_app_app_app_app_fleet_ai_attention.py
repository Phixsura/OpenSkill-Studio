"""Fleet AI Attention Mechanism — track attention pattern analysis."""
from __future__ import annotations
def fleet_ai_attention(analyzers: list[dict]) -> dict:
    active = [a for a in analyzers if a.get("active", True)]
    heads_tracked = sum(a.get("heads", 0) for a in analyzers)
    sequences_24h = sum(a.get("sequences_24h", 0) for a in analyzers)
    sparsity = round(sum(a.get("sparsity_pct", 0) for a in analyzers) / max(len(analyzers), 1), 1)
    return {"analyzers": len(analyzers), "active": len(active), "heads": heads_tracked,
            "sequences_24h": sequences_24h, "sparsity": sparsity, "efficient": sparsity > 60}
