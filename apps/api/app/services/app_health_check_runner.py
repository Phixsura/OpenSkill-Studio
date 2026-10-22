"""Health check runner — execute health checks for installed apps."""

from datetime import UTC, datetime


async def run_health_check(*, app_id: str, check_url: str | None = None) -> dict:
    """Run health check for an app (stub — actual HTTP call in production)."""
    return {
        "app_id": app_id,
        "status": "healthy",
        "latency_ms": 0,
        "checked_at": datetime.now(UTC).isoformat(),
        "check_url": check_url,
    }


def format_health_result(result: dict) -> str:
    """Format health check result as human-readable string."""
    status = result.get("status", "unknown")
    latency = result.get("latency_ms", 0)
    icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
    return f"{icon} {status} ({latency}ms)"


def aggregate_health(results: list[dict]) -> dict:
    """Aggregate multiple health check results."""
    if not results:
        return {"overall": "unknown", "checked": 0, "healthy": 0, "unhealthy": 0}
    healthy = sum(1 for r in results if r.get("status") == "healthy")
    return {
        "overall": "healthy" if healthy == len(results) else "degraded",
        "checked": len(results),
        "healthy": healthy,
        "unhealthy": len(results) - healthy,
    }
