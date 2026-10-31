"""Platform health dashboard — overall system health for the entire marketplace."""


def build_platform_health_dashboard(*, services: list[dict], app_count: int,
                                       active_installs: int, error_rate: float,
                                       avg_response_ms: int) -> dict:
    all_healthy = all(s.get("status") == "healthy" for s in services)
    return {
        "page_type": "platform_health",
        "overall": "healthy" if all_healthy and error_rate < 1 else "degraded" if error_rate < 5 else "critical",
        "metrics": {
            "apps": app_count, "active_installs": active_installs,
            "error_rate": error_rate, "avg_response_ms": avg_response_ms,
        },
        "services": services,
        "actions": ["view_logs", "restart_service", "scale_up"] if not all_healthy else [],
    }
