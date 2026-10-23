"""Command palette — searchable command palette for power users."""


COMMANDS = [
    {"id": "search", "label": "Search Apps", "shortcut": "Cmd+K", "category": "navigation", "icon": "🔍"},
    {"id": "new_app", "label": "Create New App", "shortcut": "Cmd+N", "category": "actions", "icon": "➕"},
    {"id": "deploy", "label": "Deploy App", "shortcut": "Cmd+D", "category": "actions", "icon": "🚀"},
    {"id": "settings", "label": "Settings", "shortcut": "Cmd+,", "category": "navigation", "icon": "⚙️"},
    {"id": "docs", "label": "Documentation", "shortcut": "Cmd+/", "category": "help", "icon": "📚"},
    {"id": "feedback", "label": "Send Feedback", "shortcut": None, "category": "help", "icon": "💬"},
    {"id": "logs", "label": "View Logs", "shortcut": "Cmd+L", "category": "debug", "icon": "📋"},
    {"id": "api_keys", "label": "API Keys", "shortcut": None, "category": "settings", "icon": "🔑"},
]


def search_commands(*, query: str, limit: int = 10) -> dict:
    q = query.lower().strip()
    if not q:
        return {"commands": COMMANDS[:limit], "total": len(COMMANDS)}
    matched = [c for c in COMMANDS if q in c["label"].lower() or q in c["category"]]
    return {"commands": matched[:limit], "total": len(matched), "query": query}


def get_commands_by_category() -> dict:
    by_cat: dict[str, list] = {}
    for cmd in COMMANDS:
        by_cat.setdefault(cmd["category"], []).append(cmd)
    return {"categories": [{"name": k, "commands": v} for k, v in sorted(by_cat.items())],
            "total_commands": len(COMMANDS)}
