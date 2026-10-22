"""Integration catalog — browse and discover available integrations."""


INTEGRATIONS = [
    {"id": "slack", "name": "Slack", "category": "communication", "status": "stable", "icon": "💬"},
    {"id": "github", "name": "GitHub", "category": "developer", "status": "stable", "icon": "🐙"},
    {"id": "jira", "name": "Jira", "category": "project_management", "status": "stable", "icon": "📋"},
    {"id": "notion", "name": "Notion", "category": "knowledge", "status": "beta", "icon": "📝"},
    {"id": "linear", "name": "Linear", "category": "project_management", "status": "stable", "icon": "🔷"},
    {"id": "discord", "name": "Discord", "category": "communication", "status": "beta", "icon": "🎮"},
]


def list_integrations(*, category: str | None = None, status: str | None = None) -> list[dict]:
    result = INTEGRATIONS
    if category:
        result = [i for i in result if i["category"] == category]
    if status:
        result = [i for i in result if i["status"] == status]
    return result


def search_integrations(*, query: str) -> list[dict]:
    q = query.lower()
    return [i for i in INTEGRATIONS if q in i["name"].lower() or q in i["category"]]


def get_integration(*, integration_id: str) -> dict | None:
    return next((i for i in INTEGRATIONS if i["id"] == integration_id), None)
