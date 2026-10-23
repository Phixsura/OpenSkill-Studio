"""Command palette — searchable command interface for developer console."""


COMMANDS = [
    {"id": "create_app", "label": "Create New App", "shortcut": "Ctrl+N", "category": "apps", "icon": "➕"},
    {"id": "deploy", "label": "Deploy Version", "shortcut": "Ctrl+D", "category": "apps", "icon": "🚀"},
    {"id": "view_logs", "label": "View Logs", "shortcut": "Ctrl+L", "category": "debug", "icon": "📋"},
    {"id": "open_console", "label": "Open Console", "shortcut": "Ctrl+`", "category": "debug", "icon": "💻"},
    {"id": "api_docs", "label": "API Documentation", "shortcut": "Ctrl+H", "category": "help", "icon": "📚"},
    {"id": "settings", "label": "Settings", "shortcut": "Ctrl+,", "category": "config", "icon": "⚙️"},
    {"id": "billing", "label": "Billing", "shortcut": None, "category": "config", "icon": "💳"},
    {"id": "team", "label": "Team Members", "shortcut": None, "category": "config", "icon": "👥"},
]


def search_commands(*, query: str) -> list[dict]:
    if not query:
        return COMMANDS[:6]
    q = query.lower()
    return [c for c in COMMANDS if q in c["label"].lower() or q in c.get("category", "")]


def get_commands_by_category(*, category: str) -> list[dict]:
    return [c for c in COMMANDS if c["category"] == category]


def get_recent_commands(*, history: list[str], limit: int = 5) -> list[dict]:
    recent = []
    for cmd_id in reversed(history):
        cmd = next((c for c in COMMANDS if c["id"] == cmd_id), None)
        if cmd and cmd not in recent:
            recent.append(cmd)
        if len(recent) >= limit:
            break
    return recent
