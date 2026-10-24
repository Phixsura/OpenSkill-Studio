"""Complete debug console — master aggregator for developer debugging tools."""


def build_complete_debug_console(*, app: dict, logs: list[dict], requests: list[dict],
                                    sandbox_status: dict, feature_flags: list[dict],
                                    cache_stats: dict) -> dict:
    error_logs = [l for l in logs if l.get("level") == "error"]
    failed_requests = [r for r in requests if r.get("status_code", 200) >= 400]
    return {
        "page_type": "debug_console",
        "app": {"id": app["id"], "name": app["name"]},
        "panels": [
            {"key": "logs", "title": f"Logs ({len(logs)})", "icon": "📋",
             "errors": len(error_logs), "data": {"recent": logs[:20]}},
            {"key": "requests", "title": f"Requests ({len(requests)})", "icon": "🌐",
             "failures": len(failed_requests), "data": {"recent": requests[:20]}},
            {"key": "sandbox", "title": "Sandbox", "icon": "📦", "data": sandbox_status},
            {"key": "flags", "title": f"Feature Flags ({len(feature_flags)})", "icon": "🚩",
             "data": {"flags": feature_flags}},
            {"key": "cache", "title": "Cache", "icon": "⚡", "data": cache_stats},
        ],
        "health": "degraded" if error_logs or failed_requests else "healthy",
    }
