"""Status page v2 — public-facing status page with incident history and subscriptions."""


def build_status_page_v2(*, services: list[dict], incidents: list[dict],
                            maintenance: list[dict], uptime_90d: float) -> dict:
    all_operational = all(s.get("status") == "operational" for s in services)
    active_incidents = [i for i in incidents if i.get("status") != "resolved"]
    scheduled_maintenance = [m for m in maintenance if m.get("status") == "scheduled"]
    overall = "operational" if all_operational and not active_incidents else \
              "major_outage" if any(s.get("status") == "major_outage" for s in services) else "partial_outage"
    return {
        "overall_status": overall, "services": services,
        "active_incidents": active_incidents, "recent_incidents": incidents[:5],
        "scheduled_maintenance": scheduled_maintenance,
        "uptime_90d": uptime_90d,
        "subscribe_options": ["email", "slack", "webhook", "rss"],
    }


def generate_status_embed(*, status: str, uptime: float) -> dict:
    colors = {"operational": "#22c55e", "partial_outage": "#eab308", "major_outage": "#ef4444"}
    return {"badge_color": colors.get(status, "#6b7280"), "status_text": status.replace("_", " ").title(),
            "uptime_text": f"{uptime}% uptime", "embed_html": f'<div style="color:{colors.get(status)}">{status}</div>'}
