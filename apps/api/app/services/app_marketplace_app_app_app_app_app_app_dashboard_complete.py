"""Dashboard complete — the ultimate unified developer platform dashboard."""

import html
from datetime import datetime, timezone


def build_unified_dashboard(*, user: dict, org: dict, apps: list[dict],
                               webhooks_health: str = "good",
                               deploy_status: str = "stable",
                               notifications: int = 0) -> dict:
    total_installs = sum(a.get("installs", 0) for a in apps)
    total_api = sum(a.get("api_calls", 0) for a in apps)
    avg_rating = round(sum(a.get("rating", 0) for a in apps) / max(len(apps), 1), 1)
    hour = datetime.now(timezone.utc).hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    return {
        "greeting": f"{greeting}, {html.escape(user.get('name', ''))}!",
        "org": html.escape(org.get("name", "")),
        "plan": org.get("plan", "free"),
        "health": {
            "apps": "operational" if apps else "no_apps",
            "webhooks": webhooks_health,
            "deploys": deploy_status,
            "overall": "healthy" if webhooks_health == "good" and deploy_status == "stable" else "attention",
        },
        "kpis": [
            {"label": "Apps", "value": len(apps), "icon": "📦"},
            {"label": "Installs", "value": total_installs, "display": f"{total_installs:,}", "icon": "📥"},
            {"label": "API Calls", "value": total_api, "display": f"{total_api:,}", "icon": "🔗"},
            {"label": "Avg Rating", "value": avg_rating, "display": f"⭐ {avg_rating}", "icon": "💫"},
        ],
        "notifications": notifications,
        "recent_apps": [{"id": a.get("id"), "name": html.escape(a.get("name", "")),
                          "icon": a.get("icon", "📦")} for a in apps[:3]],
    }
