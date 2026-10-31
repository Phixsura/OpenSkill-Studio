"""Complete sandbox page — master aggregator for sandbox development environment."""


def build_complete_sandbox_page(*, app: dict, sandbox_status: dict, filesystem: dict,
                                   console_history: list[dict], resource_usage: dict,
                                   network_policy: dict, logs: list[dict]) -> dict:
    return {
        "page_type": "sandbox_environment",
        "app": {"id": app["id"], "name": app["name"]},
        "sandbox": sandbox_status,
        "panels": [
            {"key": "console", "title": "Console", "icon": "💻", "data": {"history": console_history}},
            {"key": "files", "title": f"Files ({filesystem.get('files', 0)})", "icon": "📁", "data": filesystem},
            {"key": "resources", "title": "Resources", "icon": "📊", "data": resource_usage},
            {"key": "network", "title": "Network", "icon": "🌐", "data": network_policy},
            {"key": "logs", "title": f"Logs ({len(logs)})", "icon": "📋", "data": {"recent": logs[:50]}},
        ],
    }
