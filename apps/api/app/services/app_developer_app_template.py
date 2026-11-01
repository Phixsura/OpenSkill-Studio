"""App template library — pre-built app templates for quick start."""

APP_TEMPLATES = {
    "lms-connector": {
        "name": "LMS Connector",
        "category": "connector",
        "description": "Connect your LMS to OpenSkill for automatic submission syncing",
        "permissions": ["read:cohorts", "read:submissions", "write:project_results", "subscribe:events"],
        "events": ["submission.completed"],
        "secrets": [{"key": "LMS_API_KEY", "required": True}, {"key": "LMS_API_SECRET"}],
    },
    "auto-grader": {
        "name": "Auto Grader",
        "category": "automation",
        "description": "Automatically grade submissions using AI evaluation",
        "permissions": ["read:submissions", "write:evaluations", "subscribe:events", "run:background_jobs"],
        "events": ["submission.completed"],
    },
    "analytics-dashboard": {
        "name": "Analytics Dashboard",
        "category": "analytics",
        "description": "Custom analytics dashboard with cohort insights",
        "permissions": ["read:cohorts", "read:skills", "read:analytics", "extend:ui"],
    },
    "slack-notifier": {
        "name": "Slack Notifier",
        "category": "automation",
        "description": "Send Slack notifications for key platform events",
        "permissions": ["subscribe:events"],
        "events": ["submission.completed", "cohort.member_added", "project.published"],
        "secrets": [{"key": "SLACK_WEBHOOK_URL", "required": True}],
    },
}


def get_template(template_id: str) -> dict | None:
    return APP_TEMPLATES.get(template_id)


def list_templates() -> list[dict]:
    return [{"id": tid, **t} for tid, t in APP_TEMPLATES.items()]


def get_template_by_category(category: str) -> list[dict]:
    return [{"id": tid, **t} for tid, t in APP_TEMPLATES.items() if t["category"] == category]
