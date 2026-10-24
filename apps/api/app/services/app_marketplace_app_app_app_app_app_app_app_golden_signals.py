"""Golden signals dashboard — the four golden signals of monitoring."""
from __future__ import annotations


def calculate_golden_signals(latency_ms: float, traffic_rps: float,
                               error_rate_pct: float, saturation_pct: float) -> dict:
    lat_ok = latency_ms < 200
    traffic_ok = traffic_rps > 0
    err_ok = error_rate_pct < 1
    sat_ok = saturation_pct < 80
    score = sum([lat_ok, traffic_ok, err_ok, sat_ok])
    status = "healthy" if score == 4 else "degraded" if score >= 2 else "critical"
    return {"latency": {"value": latency_ms, "unit": "ms", "ok": lat_ok},
            "traffic": {"value": traffic_rps, "unit": "rps", "ok": traffic_ok},
            "errors": {"value": error_rate_pct, "unit": "%", "ok": err_ok},
            "saturation": {"value": saturation_pct, "unit": "%", "ok": sat_ok},
            "score": score, "status": status}
