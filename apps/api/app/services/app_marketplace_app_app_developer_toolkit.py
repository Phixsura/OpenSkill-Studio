"""Developer toolkit — comprehensive toolkit page for developers."""


TOOLS = [
    {"id": "api_playground", "name": "API Playground", "icon": "🎮", "category": "development", "description": "Test API endpoints interactively"},
    {"id": "webhook_debugger", "name": "Webhook Debugger", "icon": "🪝", "category": "development", "description": "Debug webhook deliveries"},
    {"id": "secret_scanner", "name": "Secret Scanner", "icon": "🔍", "category": "security", "description": "Scan code for leaked secrets"},
    {"id": "performance_profiler", "name": "Performance Profiler", "icon": "⚡", "category": "performance", "description": "Profile app performance"},
    {"id": "log_viewer", "name": "Log Viewer", "icon": "📋", "category": "debugging", "description": "Search and filter logs"},
    {"id": "schema_validator", "name": "Schema Validator", "icon": "✅", "category": "development", "description": "Validate JSON schemas"},
    {"id": "token_inspector", "name": "Token Inspector", "icon": "🔑", "category": "security", "description": "Decode and inspect JWT tokens"},
    {"id": "mock_server", "name": "Mock Server", "icon": "🎭", "category": "development", "description": "Create mock API endpoints"},
]


def get_toolkit(*, category: str | None = None) -> dict:
    filtered = TOOLS if not category else [t for t in TOOLS if t["category"] == category]
    categories = sorted(set(t["category"] for t in TOOLS))
    return {"tools": filtered, "total": len(filtered), "categories": categories}
