"""API explorer page — interactive API endpoint browser with try-it."""

import html

ENDPOINTS = [
    {"method": "GET", "path": "/api/v1/apps", "summary": "List all apps", "auth": True, "tag": "Apps"},
    {"method": "POST", "path": "/api/v1/apps", "summary": "Create app", "auth": True, "tag": "Apps"},
    {"method": "GET", "path": "/api/v1/apps/{id}", "summary": "Get app", "auth": True, "tag": "Apps"},
    {"method": "PUT", "path": "/api/v1/apps/{id}", "summary": "Update app", "auth": True, "tag": "Apps"},
    {"method": "DELETE", "path": "/api/v1/apps/{id}", "summary": "Delete app", "auth": True, "tag": "Apps"},
    {"method": "GET", "path": "/api/v1/webhooks", "summary": "List webhooks", "auth": True, "tag": "Webhooks"},
    {"method": "POST", "path": "/api/v1/webhooks", "summary": "Create webhook", "auth": True, "tag": "Webhooks"},
    {"method": "GET", "path": "/api/v1/analytics", "summary": "Get analytics", "auth": True, "tag": "Analytics"},
    {"method": "GET", "path": "/api/v1/health", "summary": "Health check", "auth": False, "tag": "System"},
    {"method": "GET", "path": "/api/v1/status", "summary": "Platform status", "auth": False, "tag": "System"},
]


def build_api_explorer_page(*, base_url: str = "https://api.openskill.dev",
                                tag_filter: str | None = None) -> dict:
    filtered = ENDPOINTS if not tag_filter else [e for e in ENDPOINTS if e["tag"] == tag_filter]
    tags = sorted(set(e["tag"] for e in ENDPOINTS))
    items = [{"method": e["method"], "path": e["path"],
              "full_url": f"{base_url}{e['path']}",
              "summary": html.escape(e["summary"]),
              "auth": e["auth"], "tag": e["tag"]} for e in filtered]
    return {"endpoints": items, "total": len(items), "tags": tags,
            "base_url": base_url, "tag_filter": tag_filter}
