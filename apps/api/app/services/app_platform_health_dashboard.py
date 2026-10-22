"""Platform health dashboard — unified health overview."""


def build_health_dashboard(*, total_apps: int, healthy_apps: int, degraded_apps: int, critical_apps: int,
                            avg_health: float, total_alerts: int) -> dict:
    return {
        "total_apps": total_apps,
        "healthy": healthy_apps, "degraded": degraded_apps, "critical": critical_apps,
        "avg_health": round(avg_health, 1),
        "total_alerts": total_alerts,
        "overall": "healthy" if critical_apps == 0 and avg_health >= 90 else "degraded" if critical_apps == 0 else "critical",
    }
