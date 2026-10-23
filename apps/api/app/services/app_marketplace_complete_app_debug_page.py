"""Complete app debug page — all debugging tools unified in one view."""


def build_complete_debug_page(*, app: dict, logs: list[dict], requests: list[dict],
                                  errors: list[dict], traces: list[dict], sandbox: dict) -> dict:
    error_count = sum(1 for l in logs if l.get("level") == "error")
    failed_requests = sum(1 for r in requests if r.get("status_code", 200) >= 400)
    return {
        "page_type": "debug_tools",
        "app": {"id": app["id"], "name": app["name"]},
        "health": "critical" if error_count > 10 else "warning" if error_count > 0 else "healthy",
        "panels": [
            {"key": "logs", "title": f"Logs ({len(logs)})", "icon": "📋", "errors": error_count},
            {"key": "requests", "title": f"Requests ({len(requests)})", "icon": "🌐", "failed": failed_requests},
            {"key": "errors", "title": f"Errors ({len(errors)})", "icon": "❌"},
            {"key": "traces", "title": f"Traces ({len(traces)})", "icon": "🔍"},
            {"key": "console", "title": "Console", "icon": "💻"},
            {"key": "sandbox", "title": "Sandbox", "icon": "🧪", "status": sandbox.get("status")},
        ],
    }
