"""Distributed tracing config — configure tracing for services."""
from __future__ import annotations

EXPORTERS = {"jaeger", "zipkin", "otlp", "console", "none"}
SAMPLERS = {"always", "never", "probability", "rate_limiting"}


def create_config(service_name: str, exporter: str = "otlp",
                   sampler: str = "probability", sample_rate: float = 0.1) -> dict:
    if exporter not in EXPORTERS:
        return {"valid": False, "error": f"unknown exporter, use {sorted(EXPORTERS)}"}
    if sampler not in SAMPLERS:
        return {"valid": False, "error": f"unknown sampler, use {sorted(SAMPLERS)}"}
    return {"valid": True, "service_name": service_name, "exporter": exporter,
            "sampler": sampler, "sample_rate": sample_rate,
            "propagation": "w3c", "max_spans_per_trace": 1000}


def estimate_volume(rps: int, sample_rate: float, avg_spans: int = 5) -> dict:
    sampled_rps = rps * sample_rate
    spans_per_sec = sampled_rps * avg_spans
    daily = int(spans_per_sec * 86400)
    storage_gb = round(daily * 0.001 / 1_000_000, 2)  # ~1KB per span
    return {"rps": rps, "sampled_rps": round(sampled_rps, 1),
            "spans_per_sec": round(spans_per_sec, 1),
            "daily_spans": daily, "storage_gb_day": storage_gb}
