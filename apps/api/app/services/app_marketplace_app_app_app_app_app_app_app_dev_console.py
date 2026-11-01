"""Developer console overview — unified developer dashboard data."""
from __future__ import annotations
import html


def build_dev_console(*, developer: dict, apps: list[dict],
                        recent_deploys: list[dict], open_issues: int = 0,
                        api_calls_today: int = 0) -> dict:
    total_installs = sum(a.get("installs", 0) for a in apps)
    avg_rating = round(sum(a.get("rating", 0) for a in apps) / max(len(apps), 1), 1)
    return {
        "developer": {
            "name": html.escape(developer.get("name", "")),
            "plan": developer.get("plan", "free"),
            "verified": developer.get("verified", False),
        },
        "apps_summary": {
            "total": len(apps), "total_installs": total_installs,
            "installs_display": f"{total_installs:,}",
            "avg_rating": avg_rating,
        },
        "recent_deploys": [{"app": html.escape(d.get("app", "")),
                              "version": d.get("version", ""),
                              "status": d.get("status", ""),
                              "time": d.get("time", "")}
                             for d in recent_deploys[:5]],
        "open_issues": open_issues,
        "api_calls_today": api_calls_today,
        "api_display": f"{api_calls_today:,}",
        "quick_actions": [
            {"label": "Create App", "icon": "📱", "action": "create_app"},
            {"label": "View Docs", "icon": "📚", "action": "view_docs"},
            {"label": "API Keys", "icon": "🔑", "action": "api_keys"},
            {"label": "Deploy", "icon": "🚀", "action": "deploy"},
        ],
    }
