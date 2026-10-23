"""App health dashboard v3 — unified health view with SLI/SLO tracking."""


def build_health_dashboard_v3(*, app: dict, slis: list[dict], slos: list[dict],
                                  incidents: list[dict], uptime_history: list[dict]) -> dict:
    active_incidents = [i for i in incidents if i.get("status") != "resolved"]
    slo_violations = [s for s in slos if s.get("current") < s.get("target")]
    health = "critical" if active_incidents else "warning" if slo_violations else "healthy"
    return {
        "page_type": "health_dashboard_v3",
        "app": {"id": app["id"], "name": app["name"]},
        "health": health,
        "panels": [
            {"key": "overview", "title": "Health Status", "status": health, "icon": "💚" if health == "healthy" else "⚠️"},
            {"key": "slis", "title": f"SLIs ({len(slis)})", "data": slis},
            {"key": "slos", "title": f"SLOs ({len(slo_violations)} violations)", "data": slos},
            {"key": "incidents", "title": f"Incidents ({len(active_incidents)} active)", "data": incidents[:10]},
            {"key": "uptime", "title": "Uptime History", "data": uptime_history[:30]},
        ],
    }


def compute_error_budget_v2(*, slo_target: float, actual: float, period_requests: int) -> dict:
    allowed_errors = int(period_requests * (1 - slo_target / 100))
    actual_errors = int(period_requests * (1 - actual / 100))
    remaining = max(0, allowed_errors - actual_errors)
    pct = round(remaining / max(allowed_errors, 1) * 100, 1)
    return {"allowed": allowed_errors, "consumed": actual_errors, "remaining": remaining,
            "remaining_pct": pct, "exhausted": remaining <= 0}
