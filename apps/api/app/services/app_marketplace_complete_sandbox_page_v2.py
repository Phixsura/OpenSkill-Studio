"""Complete sandbox page v2 — full sandbox development environment."""


def build_complete_sandbox_page_v2(*, app: dict, sandbox: dict, console_history: list[dict],
                                       filesystem: dict, resources: dict, network: dict,
                                       snapshots: list[dict]) -> dict:
    return {
        "page_type": "sandbox_v2",
        "app": {"id": app["id"], "name": app["name"]},
        "sandbox": {"status": sandbox.get("status", "stopped"), "uptime_minutes": sandbox.get("uptime", 0)},
        "panels": [
            {"key": "console", "title": "Console", "icon": "💻", "history_count": len(console_history)},
            {"key": "files", "title": f"Files ({filesystem.get('file_count', 0)})", "icon": "📁"},
            {"key": "resources", "title": "Resources", "icon": "📊", "data": resources},
            {"key": "network", "title": "Network", "icon": "🌐", "data": network},
            {"key": "snapshots", "title": f"Snapshots ({len(snapshots)})", "icon": "📸"},
            {"key": "logs", "title": "Logs", "icon": "📋"},
        ],
        "actions": {"start": sandbox.get("status") != "running", "stop": sandbox.get("status") == "running",
                      "restart": sandbox.get("status") == "running", "snapshot": True},
    }
