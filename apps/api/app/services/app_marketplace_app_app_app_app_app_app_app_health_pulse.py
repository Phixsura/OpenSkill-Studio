"""Platform health pulse — lightweight periodic health summary."""
from __future__ import annotations


def compute_pulse(*, api_ok: bool, db_ok: bool, cache_ok: bool,
                    queue_ok: bool, storage_ok: bool,
                    active_incidents: int = 0, error_rate_pct: float = 0,
                    p99_latency_ms: float = 0) -> dict:
    checks = {"api": api_ok, "database": db_ok, "cache": cache_ok,
              "queue": queue_ok, "storage": storage_ok}
    healthy = sum(1 for v in checks.values() if v)
    total = len(checks)
    score = round(healthy / total * 100)
    if active_incidents > 0 or error_rate_pct > 5:
        status = "critical"
    elif not all(checks.values()) or error_rate_pct > 1:
        status = "degraded"
    elif p99_latency_ms > 500:
        status = "slow"
    else:
        status = "healthy"
    emoji = {"healthy": "💚", "degraded": "💛", "slow": "🟠", "critical": "❤️‍🔥"}.get(status, "⚪")
    return {
        "status": status, "emoji": emoji, "score": score,
        "score_display": f"{score}%",
        "checks": checks, "healthy_count": healthy, "total_checks": total,
        "active_incidents": active_incidents,
        "error_rate_pct": error_rate_pct,
        "p99_latency_ms": p99_latency_ms,
        "summary": f"{emoji} {status.upper()} — {healthy}/{total} services · {error_rate_pct}% errors · {p99_latency_ms}ms p99",
    }
