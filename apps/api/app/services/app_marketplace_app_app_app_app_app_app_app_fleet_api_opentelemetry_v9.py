"""Fleet API OpenTelemetry v9 — track OTel instrumentation coverage."""
from __future__ import annotations
def fleet_api_opentelemetry_v9(services: list[dict]) -> dict:
    instrumented = [s for s in services if s.get("otel_enabled")]
    traces = sum(s.get("traces_per_sec", 0) for s in services)
    metrics = sum(s.get("metrics_per_sec", 0) for s in services)
    return {"services": len(services), "instrumented": len(instrumented), "traces_per_sec": traces,
            "metrics_per_sec": metrics, "healthy": len(instrumented) == len(services)}
