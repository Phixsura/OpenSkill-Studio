"""Endpoint monitor — continuous monitoring of API endpoints."""

from datetime import datetime, timedelta


def check_endpoint(*, url: str, expected_status: int = 200,
                     timeout_ms: int = 5000) -> dict:
    # Simulated check
    actual_status = 200
    latency = 42
    return {
        "url": url,
        "expected_status": expected_status,
        "actual_status": actual_status,
        "latency_ms": latency,
        "healthy": actual_status == expected_status and latency < timeout_ms,
        "checked_at": datetime.utcnow().isoformat(),
    }


def get_monitor_summary(*, checks: list[dict], period_hours: int = 24) -> dict:
    total = len(checks)
    healthy = sum(1 for c in checks if c.get("healthy"))
    avg_latency = round(sum(c.get("latency_ms", 0) for c in checks) / max(total, 1), 1)
    uptime_pct = round(healthy / max(total, 1) * 100, 2)
    by_url: dict[str, dict] = {}
    for c in checks:
        url = c.get("url", "")
        if url not in by_url:
            by_url[url] = {"checks": 0, "healthy": 0, "total_latency": 0}
        by_url[url]["checks"] += 1
        if c.get("healthy"):
            by_url[url]["healthy"] += 1
        by_url[url]["total_latency"] += c.get("latency_ms", 0)
    endpoints = [{"url": u, "uptime_pct": round(d["healthy"] / d["checks"] * 100, 1),
                   "avg_latency_ms": round(d["total_latency"] / d["checks"], 1)}
                  for u, d in by_url.items()]
    return {"total_checks": total, "uptime_pct": uptime_pct, "avg_latency_ms": avg_latency,
            "endpoints": endpoints, "period_hours": period_hours}
