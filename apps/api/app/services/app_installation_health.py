"""Installation health — aggregate health across all installations of an app."""


def aggregate_installation_health(installations: list[dict]) -> dict:
    """Aggregate health across installations."""
    if not installations:
        return {"total": 0, "healthy": 0, "degraded": 0, "critical": 0, "overall": "unknown"}
    
    healthy = sum(1 for i in installations if i.get("health_score", 100) >= 80)
    degraded = sum(1 for i in installations if 50 <= i.get("health_score", 100) < 80)
    critical = sum(1 for i in installations if i.get("health_score", 100) < 50)
    
    if critical > 0:
        overall = "critical"
    elif degraded > len(installations) * 0.3:
        overall = "degraded"
    else:
        overall = "healthy"
    
    return {"total": len(installations), "healthy": healthy, "degraded": degraded, "critical": critical, "overall": overall}
