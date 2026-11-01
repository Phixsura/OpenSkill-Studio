"""Complete platform health FINAL — comprehensive health status for the entire platform."""


def build_platform_health_final(*, services: list[dict], uptime: dict,
                                     error_budget: dict, incidents: list[dict],
                                     deployment: dict, infrastructure: dict) -> dict:
    all_healthy = all(s.get("status") == "healthy" for s in services)
    active_incidents = [i for i in incidents if i.get("status") != "resolved"]
    overall = "healthy" if all_healthy and not active_incidents else \
              "critical" if any(s.get("status") == "down" for s in services) else "degraded"
    return {
        "page_type": "platform_health_final",
        "overall": overall,
        "uptime": uptime,
        "services": services,
        "service_count": len(services),
        "healthy_count": sum(1 for s in services if s.get("status") == "healthy"),
        "active_incidents": active_incidents,
        "error_budget": error_budget,
        "deployment": deployment,
        "infrastructure": infrastructure,
    }
