"""Fleet Distributed Tracing v9 — track end-to-end request tracing."""
from __future__ import annotations
def fleet_distributed_tracing_v9(services: list[dict]) -> dict:
    instrumented = [s for s in services if s.get("tracing_enabled")]
    spans_per_sec = sum(s.get("spans_per_sec", 0) for s in services)
    sampling_rate = sum(s.get("sampling_rate", 0) for s in services) / len(services) if services else 0
    return {"services": len(services), "instrumented": len(instrumented), "spans_per_sec": spans_per_sec,
            "avg_sampling_rate": round(sampling_rate, 1), "healthy": len(instrumented) == len(services)}
