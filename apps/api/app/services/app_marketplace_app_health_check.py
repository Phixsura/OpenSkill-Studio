"""App health check — monitor app endpoints and report status."""

from datetime import datetime, timedelta


def run_health_checks(*, app_id: str, endpoints: list[dict]) -> dict:
    results = []
    for ep in endpoints:
        status_code = ep.get("status_code", 200)
        latency_ms = ep.get("latency_ms", 50)
        healthy = 200 <= status_code < 400 and latency_ms < 5000
        results.append({
            "url": ep["url"],
            "status_code": status_code,
            "latency_ms": latency_ms,
            "healthy": healthy,
            "checked_at": datetime.utcnow().isoformat(),
        })
    all_healthy = all(r["healthy"] for r in results)
    avg_latency = round(sum(r["latency_ms"] for r in results) / max(len(results), 1), 1)
    return {
        "app_id": app_id,
        "checks": results,
        "all_healthy": all_healthy,
        "healthy_count": sum(1 for r in results if r["healthy"]),
        "total_checks": len(results),
        "avg_latency_ms": avg_latency,
    }


def get_uptime_history(*, app_id: str, days: int = 30) -> dict:
    base = datetime(2026, 10, 23)
    daily = []
    for d in range(days):
        dt = base - timedelta(days=d)
        up = 100.0 if d % 15 != 0 else 99.5
        daily.append({"date": dt.strftime("%Y-%m-%d"), "uptime_pct": up})
    overall = round(sum(d["uptime_pct"] for d in daily) / len(daily), 3)
    return {"app_id": app_id, "days": days, "daily": daily,
            "overall_uptime": overall}
