"""Golden signals — monitor the four golden signals of monitoring."""
from __future__ import annotations


def evaluate_golden_signals(metrics: dict) -> dict:
    # Latency
    latency_ms = metrics.get("p99_ms", 0)
    latency_ok = latency_ms < metrics.get("latency_target_ms", 500)
    # Traffic
    rps = metrics.get("rps", 0)
    traffic_ok = rps > 0
    # Errors
    error_rate = metrics.get("error_rate_pct", 0)
    errors_ok = error_rate < metrics.get("error_target_pct", 1)
    # Saturation
    cpu_pct = metrics.get("cpu_pct", 0)
    mem_pct = metrics.get("memory_pct", 0)
    saturation = max(cpu_pct, mem_pct)
    saturation_ok = saturation < 80

    all_ok = latency_ok and traffic_ok and errors_ok and saturation_ok
    status = "healthy" if all_ok else "degraded"
    return {"status": status,
            "latency": {"p99_ms": latency_ms, "ok": latency_ok},
            "traffic": {"rps": rps, "ok": traffic_ok},
            "errors": {"rate_pct": error_rate, "ok": errors_ok},
            "saturation": {"pct": saturation, "ok": saturation_ok}}
