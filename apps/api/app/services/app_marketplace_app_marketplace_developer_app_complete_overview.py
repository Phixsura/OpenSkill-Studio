"""Complete developer app overview — the ultimate single-page summary of an app for developers.

This aggregator combines every dimension of app management into one view:
status, health, analytics, reviews, webhooks, team, billing, and compliance.
"""


def build_complete_app_overview(*, app: dict, health: dict, analytics: dict,
                                    reviews: dict, webhooks: dict, team: dict,
                                    billing: dict, compliance: dict) -> dict:
    # Compute overall health grade
    scores = [health.get("score", 0), analytics.get("engagement_score", 0),
              reviews.get("avg_rating", 0) * 20, compliance.get("score", 0)]
    overall = round(sum(scores) / max(len(scores), 1), 1)
    grade = "A" if overall >= 90 else "B" if overall >= 75 else "C" if overall >= 60 else "D"

    return {
        "page_type": "app_complete_overview",
        "app": {"id": app["id"], "name": app["name"], "status": app.get("status"),
                "version": app.get("current_version"), "slug": app.get("slug")},
        "overall_grade": grade, "overall_score": overall,
        "sections": [
            {"key": "health", "title": "Health", "icon": "💚", "score": health.get("score", 0),
             "status": health.get("status", "unknown")},
            {"key": "analytics", "title": "Analytics", "icon": "📊",
             "highlights": [f"{analytics.get('installs', 0)} installs",
                             f"{analytics.get('api_calls', 0)} API calls"]},
            {"key": "reviews", "title": "Reviews", "icon": "⭐",
             "rating": reviews.get("avg_rating", 0), "count": reviews.get("count", 0)},
            {"key": "webhooks", "title": "Webhooks", "icon": "🔗",
             "active": webhooks.get("active", 0), "delivery_rate": webhooks.get("delivery_rate", 0)},
            {"key": "team", "title": "Team", "icon": "👥", "members": team.get("member_count", 0)},
            {"key": "billing", "title": "Billing", "icon": "💳",
             "plan": billing.get("plan", "free"), "mrr": billing.get("mrr", "$0")},
            {"key": "compliance", "title": "Compliance", "icon": "📋",
             "score": compliance.get("score", 0), "compliant": compliance.get("compliant", False)},
        ],
        "quick_actions": [
            {"id": "deploy", "label": "Deploy New Version", "icon": "🚀"},
            {"id": "analytics", "label": "View Analytics", "icon": "📊"},
            {"id": "settings", "label": "App Settings", "icon": "⚙️"},
            {"id": "docs", "label": "Documentation", "icon": "📚"},
        ],
    }
