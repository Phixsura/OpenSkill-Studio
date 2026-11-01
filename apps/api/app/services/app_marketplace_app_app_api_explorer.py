"""API explorer — interactive API endpoint browser."""

import html

ENDPOINTS = [
    {"method": "GET", "path": "/api/v1/apps", "summary": "List all apps", "auth": True, "tags": ["apps"]},
    {"method": "POST", "path": "/api/v1/apps", "summary": "Create an app", "auth": True, "tags": ["apps"]},
    {"method": "GET", "path": "/api/v1/apps/{id}", "summary": "Get app by ID", "auth": True, "tags": ["apps"]},
    {"method": "PUT", "path": "/api/v1/apps/{id}", "summary": "Update app", "auth": True, "tags": ["apps"]},
    {"method": "DELETE", "path": "/api/v1/apps/{id}", "summary": "Delete app", "auth": True, "tags": ["apps"]},
    {"method": "GET", "path": "/api/v1/users/me", "summary": "Get current user", "auth": True, "tags": ["users"]},
    {"method": "GET", "path": "/api/v1/health", "summary": "Health check", "auth": False, "tags": ["system"]},
    {"method": "POST", "path": "/api/v1/webhooks", "summary": "Create webhook", "auth": True, "tags": ["webhooks"]},
]


def list_endpoints(*, tag: str | None = None, auth_only: bool = False) -> dict:
    filtered = ENDPOINTS
    if tag:
        filtered = [e for e in filtered if tag in e.get("tags", [])]
    if auth_only:
        filtered = [e for e in filtered if e.get("auth")]
    items = [{"method": e["method"], "path": e["path"],
              "summary": html.escape(e["summary"]), "auth": e["auth"],
              "tags": e["tags"]} for e in filtered]
    tags = sorted(set(t for e in ENDPOINTS for t in e.get("tags", [])))
    return {"endpoints": items, "total": len(items), "tags": tags}
