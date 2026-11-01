"""User dashboard summary — personalized dashboard data aggregation."""
from __future__ import annotations
import html


def build_user_dashboard(*, user_name: str, org_name: str, plan: str,
                            app_count: int, api_calls_today: int,
                            unread_notifications: int, recent_deploys: int,
                            health_score: int, open_tickets: int) -> dict:
    name = html.escape(user_name)
    greeting = f"Good day, {name}!"
    quick_stats = [
        {"icon": "📱", "value": str(app_count), "label": "Apps"},
        {"icon": "📡", "value": f"{api_calls_today:,}", "label": "API Calls Today"},
        {"icon": "🚀", "value": str(recent_deploys), "label": "Recent Deploys"},
        {"icon": "🔔", "value": str(unread_notifications), "label": "Notifications"},
        {"icon": "💚", "value": f"{health_score}/100", "label": "Health"},
        {"icon": "🎫", "value": str(open_tickets), "label": "Open Tickets"},
    ]
    alerts = []
    if health_score < 70:
        alerts.append({"type": "warning", "message": "Platform health needs attention"})
    if unread_notifications > 10:
        alerts.append({"type": "info", "message": f"You have {unread_notifications} unread notifications"})
    return {
        "greeting": greeting, "org_name": html.escape(org_name), "plan": plan,
        "quick_stats": quick_stats, "alerts": alerts,
    }
