"""Fleet Trace Sampling v9 — track distributed tracing sampling strategies."""
from __future__ import annotations
def fleet_trace_sampling_v9(strategies: list[dict]) -> dict:
    active = [s for s in strategies if s.get("active")]
    sample_rate = sum(s.get("rate_pct", 0) for s in strategies) / len(strategies) if strategies else 0
    traces_sampled = sum(s.get("sampled_today", 0) for s in strategies)
    return {"strategies": len(strategies), "active": len(active), "avg_rate_pct": round(sample_rate, 1),
            "sampled_today": traces_sampled, "healthy": True}
