"""Fleet trace sampler — track distributed tracing sampling rates."""
from __future__ import annotations
def fleet_trace_sampler(services: list[dict]) -> dict:
    total_spans = sum(s.get("spans_per_sec", 0) for s in services)
    sampled = sum(s.get("sampled_per_sec", 0) for s in services)
    rate = round(sampled / max(total_spans, 1) * 100, 1)
    return {"total_spans_per_sec": total_spans, "sampled_per_sec": sampled,
            "sample_rate_pct": rate, "adequate": rate >= 1}
