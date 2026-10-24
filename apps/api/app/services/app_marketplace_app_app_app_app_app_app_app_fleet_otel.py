"""Fleet OpenTelemetry — track OTel instrumentation adoption."""
from __future__ import annotations
def fleet_otel_adoption(services: list[dict]) -> dict:
    instrumented = [s for s in services if s.get("otel_instrumented", False)]
    auto = [s for s in instrumented if s.get("auto_instrumented", False)]
    pct = round(len(instrumented) / max(len(services), 1) * 100, 1)
    return {"total": len(services), "instrumented": len(instrumented), "auto": len(auto),
            "manual": len(instrumented) - len(auto), "coverage_pct": pct, "mature": pct >= 80}
