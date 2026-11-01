"""Uptime monitor — continuous uptime tracking with SLA reporting."""

from datetime import datetime, timezone


def record_check(*, endpoint: str, status_code: int, response_ms: int) -> dict:
    healthy = 200 <= status_code < 300 and response_ms < 10000
    return {"endpoint": endpoint, "status_code": status_code, "response_ms": response_ms,
            "healthy": healthy, "checked_at": datetime.now(timezone.utc).isoformat()}


def compute_uptime_stats(*, checks: list[dict], period_label: str = "30d") -> dict:
    if not checks:
        return {"uptime_pct": 100.0, "checks": 0, "period": period_label}
    healthy = sum(1 for c in checks if c.get("healthy"))
    avg_ms = round(sum(c.get("response_ms", 0) for c in checks) / len(checks))
    return {"uptime_pct": round(healthy / len(checks) * 100, 3), "checks": len(checks),
            "healthy": healthy, "avg_response_ms": avg_ms, "period": period_label,
            "downtime_minutes": round((len(checks) - healthy) * 1)}


def build_uptime_calendar(*, daily_uptimes: list[dict]) -> list[dict]:
    return [{"date": d["date"],
             "uptime_pct": d["uptime_pct"],
             "status": "good" if d["uptime_pct"] >= 99.9 else "degraded" if d["uptime_pct"] >= 99 else "outage"}
            for d in daily_uptimes[-90:]]
