"""Fleet API Observability v9 — unified API metrics, logs, and traces."""
from __future__ import annotations
def fleet_api_observability_v9(apis: list[dict]) -> dict:
    instrumented = [a for a in apis if a.get("instrumented")]
    traces_enabled = [a for a in apis if a.get("tracing")]
    metrics_enabled = [a for a in apis if a.get("metrics")]
    logs_structured = [a for a in apis if a.get("structured_logs")]
    return {"apis": len(apis), "instrumented": len(instrumented), "tracing": len(traces_enabled),
            "metrics": len(metrics_enabled), "structured_logs": len(logs_structured),
            "healthy": len(instrumented) == len(apis)}
