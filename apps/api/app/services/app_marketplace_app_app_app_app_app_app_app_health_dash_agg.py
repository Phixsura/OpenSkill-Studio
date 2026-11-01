"""Service health dashboard aggregator — aggregate health from all signals."""
from __future__ import annotations


def aggregate_health_dashboard(signals: dict) -> dict:
    checks = {
        "uptime": signals.get("uptime_pct", 100) >= 99.9,
        "error_rate": signals.get("error_rate_pct", 0) < 1,
        "latency": signals.get("p99_ms", 0) < 500,
        "saturation": signals.get("cpu_pct", 0) < 80,
        "dependencies": signals.get("deps_healthy", True),
    }
    passing = sum(1 for v in checks.values() if v)
    score = round(passing / len(checks) * 100)
    status = "healthy" if passing == len(checks) else ("degraded" if passing >= 3 else "critical")
    return {"status": status, "score": score, "checks": checks,
            "passing": passing, "total_checks": len(checks)}
