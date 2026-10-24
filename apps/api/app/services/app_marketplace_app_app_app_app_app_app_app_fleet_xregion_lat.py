"""Fleet cross-region latency — measure inter-region communication."""
from __future__ import annotations
def fleet_xregion_latency(pairs: list[dict]) -> dict:
    avg = round(sum(p.get("latency_ms", 0) for p in pairs) / max(len(pairs), 1), 1)
    high = [p for p in pairs if p.get("latency_ms", 0) > 200]
    return {"pairs": len(pairs), "avg_latency_ms": avg, "high_latency": len(high),
            "acceptable": len(high) == 0}
