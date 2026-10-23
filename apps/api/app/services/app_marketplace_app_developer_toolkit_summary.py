"""Developer toolkit summary — overview of all available developer tools."""

TOOLKIT = {
    "build": [
        {"name": "SDK", "languages": ["TypeScript", "Python"], "icon": "📦"},
        {"name": "CLI", "description": "Command-line tools", "icon": "💻"},
        {"name": "Templates", "description": "Starter templates", "icon": "📋"},
    ],
    "test": [
        {"name": "Sandbox", "description": "Isolated test environment", "icon": "🧪"},
        {"name": "Mock Server", "description": "API mocking", "icon": "🎭"},
        {"name": "Contract Tests", "description": "API contract validation", "icon": "📝"},
    ],
    "deploy": [
        {"name": "Pipeline", "description": "CI/CD automation", "icon": "🚀"},
        {"name": "Canary", "description": "Gradual rollout", "icon": "🐤"},
        {"name": "Multi-Region", "description": "Global deployment", "icon": "🌍"},
    ],
    "monitor": [
        {"name": "Dashboards", "description": "Real-time metrics", "icon": "📊"},
        {"name": "Alerts", "description": "Threshold alerts", "icon": "🔔"},
        {"name": "Tracing", "description": "Distributed tracing", "icon": "🔍"},
    ],
}

def get_toolkit_summary() -> dict:
    total = sum(len(tools) for tools in TOOLKIT.values())
    return {"categories": list(TOOLKIT.keys()), "tools": TOOLKIT, "total_tools": total}

def get_tools_by_category(*, category: str) -> list[dict]:
    return TOOLKIT.get(category, [])
