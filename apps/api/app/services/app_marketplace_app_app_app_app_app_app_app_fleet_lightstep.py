"""Fleet Lightstep — track distributed tracing and change intelligence."""
from __future__ import annotations
def fleet_lightstep_status(services: list[dict]) -> dict:
    instrumented = [s for s in services if s.get("instrumented", False)]
    latency_regression = [s for s in services if s.get("latency_regression", False)]
    return {"total": len(services), "instrumented": len(instrumented),
            "latency_regressions": len(latency_regression),
            "coverage_pct": round(len(instrumented) / max(len(services), 1) * 100, 1)}
