"""Template gallery — starter templates for new app development."""

TEMPLATES = [
    {"id": "basic-connector", "name": "Basic Connector", "category": "connector",
     "description": "Simple integration connector with OAuth", "difficulty": "beginner",
     "files": ["manifest.json", "index.ts", "auth.ts"], "stars": 150},
    {"id": "webhook-handler", "name": "Webhook Handler", "category": "automation",
     "description": "Process incoming webhooks with retry logic", "difficulty": "intermediate",
     "files": ["manifest.json", "handler.ts", "queue.ts", "retry.ts"], "stars": 89},
    {"id": "analytics-dashboard", "name": "Analytics Dashboard", "category": "analytics",
     "description": "Full-featured analytics with charts and exports", "difficulty": "advanced",
     "files": ["manifest.json", "dashboard.tsx", "charts.ts", "export.ts"], "stars": 200},
    {"id": "slack-bot", "name": "Slack Bot", "category": "communication",
     "description": "Interactive Slack bot with slash commands", "difficulty": "intermediate",
     "files": ["manifest.json", "bot.ts", "commands.ts", "events.ts"], "stars": 175},
]


def list_templates(*, category: str | None = None, difficulty: str | None = None) -> list[dict]:
    result = TEMPLATES
    if category:
        result = [t for t in result if t["category"] == category]
    if difficulty:
        result = [t for t in result if t["difficulty"] == difficulty]
    return sorted(result, key=lambda t: -t["stars"])


def get_template(*, template_id: str) -> dict | None:
    return next((t for t in TEMPLATES if t["id"] == template_id), None)


def scaffold_from_template(*, template_id: str, app_name: str, developer_id: str) -> dict:
    tmpl = get_template(template_id=template_id)
    if not tmpl:
        return {"error": f"Template '{template_id}' not found"}
    return {
        "app_name": app_name, "developer_id": developer_id,
        "template": tmpl["name"], "files_created": tmpl["files"],
        "category": tmpl["category"], "status": "scaffolded", "error": None,
    }
