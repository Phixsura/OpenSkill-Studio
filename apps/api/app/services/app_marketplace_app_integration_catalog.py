"""Integration catalog — browse and connect third-party integrations."""


INTEGRATIONS = [
    {"id": "slack", "name": "Slack", "icon": "💬", "category": "communication",
     "description": "Send notifications to Slack channels", "popular": True},
    {"id": "github", "name": "GitHub", "icon": "🐙", "category": "development",
     "description": "Sync with GitHub repos and issues", "popular": True},
    {"id": "stripe", "name": "Stripe", "icon": "💳", "category": "payments",
     "description": "Process payments and subscriptions", "popular": True},
    {"id": "zapier", "name": "Zapier", "icon": "⚡", "category": "automation",
     "description": "Connect to 5000+ apps via Zapier", "popular": False},
    {"id": "jira", "name": "Jira", "icon": "📋", "category": "project_management",
     "description": "Track issues and sprints", "popular": False},
    {"id": "datadog", "name": "Datadog", "icon": "📊", "category": "monitoring",
     "description": "Monitor app performance and logs", "popular": False},
]


def list_integrations(*, category: str | None = None, search: str | None = None) -> dict:
    results = INTEGRATIONS
    if category:
        results = [i for i in results if i["category"] == category]
    if search:
        q = search.lower()
        results = [i for i in results if q in i["name"].lower() or q in i["description"].lower()]
    categories = sorted(set(i["category"] for i in INTEGRATIONS))
    return {"integrations": results, "total": len(results),
            "categories": categories, "popular": [i for i in results if i.get("popular")]}


def connect_integration(*, app_id: str, integration_id: str,
                          config: dict | None = None) -> dict:
    integration = next((i for i in INTEGRATIONS if i["id"] == integration_id), None)
    if not integration:
        return {"success": False, "error": f"Unknown integration: {integration_id}"}
    return {"success": True, "app_id": app_id, "integration": integration["name"],
            "status": "connected", "config": config or {}}
