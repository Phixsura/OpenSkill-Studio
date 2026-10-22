"""Health check endpoint — validate app health endpoints for monitoring."""

from datetime import datetime, timezone


def build_health_check_config(*, app_id: str, endpoint: str, interval_seconds: int = 60,
                                 timeout_ms: int = 5000, expected_status: int = 200) -> dict:
    if interval_seconds < 10:
        return {"error": "Minimum interval is 10 seconds"}
    if timeout_ms > 30000:
        return {"error": "Maximum timeout is 30 seconds"}
    return {
        "app_id": app_id, "endpoint": endpoint, "interval_seconds": interval_seconds,
        "timeout_ms": timeout_ms, "expected_status": expected_status,
        "status": "active", "error": None,
    }


def evaluate_health_result(*, status_code: int, response_time_ms: int, expected_status: int,
                              timeout_ms: int) -> dict:
    healthy = status_code == expected_status and response_time_ms < timeout_ms
    return {
        "healthy": healthy, "status_code": status_code, "response_time_ms": response_time_ms,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "issues": [] if healthy else
            (["Wrong status code"] if status_code != expected_status else []) +
            (["Response too slow"] if response_time_ms >= timeout_ms else []),
    }


def compute_availability(*, results: list[dict], window_hours: int = 24) -> dict:
    if not results:
        return {"availability_pct": 100.0, "checks": 0}
    healthy = sum(1 for r in results if r.get("healthy"))
    return {"availability_pct": round(healthy / len(results) * 100, 2), "checks": len(results)}
