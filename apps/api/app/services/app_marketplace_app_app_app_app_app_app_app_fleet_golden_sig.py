"""Fleet golden signals — the four golden signals of monitoring."""
from __future__ import annotations
def fleet_golden_signals(latency_ms: float, traffic_rps: float, errors_pct: float, saturation_pct: float) -> dict:
    status = "healthy"
    if errors_pct > 5 or saturation_pct > 90:
        status = "critical"
    elif latency_ms > 500 or errors_pct > 1:
        status = "degraded"
    return {"latency_ms": latency_ms, "traffic_rps": traffic_rps,
            "errors_pct": errors_pct, "saturation_pct": saturation_pct, "status": status}
